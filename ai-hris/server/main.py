from flask import Flask, request, jsonify
from datetime import datetime
import os
from src.usecase.cv_extractor import CVExtractor
from src.config.env import AppConfig
from src.llm.llm_sk import LLMService
import asyncio
from src.domain.http_response import ok, bad_request_error, internal_server_error
from src.common.const import AssessmentType
from src.usecase.cv_scoring import CVScoring
from src.usecase.candidate_recommendation import CandidateRecommendation
from src.repository.database import CosmosDB
from src.repository.embedding import AzureAIEmbedding
from src.domain.candidate_recommendation import CandidateData, JobData
from pydantic import ValidationError
from src.repository.database import CosmosDB
from src.usecase.candidate_service import CandidateService
from src.usecase.employee_service import EmployeeService
from src.repository.document_intelligence import DocumentIntelligenceRepository
from src.repository.blob_storage import BlobStorageRepository
from src.usecase.document_analyzer import DocumentAnalyzer
from src.domain.document_analyzer import LegalDocumentResponse

app = Flask(__name__)

config = AppConfig()

cosmosdb = CosmosDB(config=config)
azembedding = AzureAIEmbedding(config=config)

llm = LLMService(
    service_id="eyds-hris-ai",
    azure_openai_deployment=config.AZURE_OPENAI_DEPLOYMENT_NAME,
    azure_openai_endpoint=config.AZURE_OPENAI_API_BASE,
    azure_openai_version=config.AZURE_OPENAI_API_VERSION,
    azure_openai_key=config.AZURE_OPENAI_API_KEY
)

document_intelligence = DocumentIntelligenceRepository(config=config)
blob_storage = BlobStorageRepository(connection_string=config.AZURE_STORAGE_CONNECTION_STRING)

cv_scoring = CVScoring(llm_service=llm)
cv_extractor = CVExtractor(llm_service=llm)
candidate_recommendation = CandidateRecommendation(cosmosdb=cosmosdb, embedding_service=azembedding)
candidate_service = CandidateService(cosmosdb=cosmosdb, llm_service=llm)
employee_service = EmployeeService(cosmosdb=cosmosdb, llm_service=llm)

document_analyzer = DocumentAnalyzer(doc_intel_repo=document_intelligence, llm_service=llm)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/v1/hr/candidate/assessment', methods=['POST'])
def candidate_assessment():
    try:
        data = request.get_json()
        assessment_type = data.get('assessment_type', AssessmentType.PredefinedScore)
        predefined_score = data.get('predefined_score')
        candidate_id = data.get('candidate_id')
        candidate_data = data.get('candidate_data')

        if assessment_type not in [AssessmentType.PredefinedScore, AssessmentType.OnlineBackgroundCheck]:
            return bad_request_error(f"Invalid assessment type: {assessment_type}")
        
        if not assessment_type:
            return bad_request_error("assessment_type is required")
        
        if assessment_type == AssessmentType.PredefinedScore and not predefined_score:
            return bad_request_error("predefined_score is required for predefined score assessment")

        if not candidate_data:
            return bad_request_error("candidate_data is required")
        
        response = asyncio.run(cv_scoring.assess(predefined_score=predefined_score, candidate_data=candidate_data))
        
        return ok(message="Candidate assessment processed successfully", data=response)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/v1/hr/resume-parser/file', methods=['POST'])
def resume_parser_file():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        response = asyncio.run(cv_extractor.extract(pdf_bytes=file.read(), pdf_file_path=file.filename))
        
        return ok(message="CV data structured successfully", data=response)
            
    except Exception as e:
        return internal_server_error(str(e))

@app.route('/api/v1/hr/resume-parser/base64', methods=['POST'])
def resume_parser_base64():
    try:
        data = request.get_json()
        
        resume = data.get('resume')

        if not resume:
            return jsonify({'error': 'resume is required'}), 400

        response = asyncio.run(cv_extractor.extract(base64_cv=resume))
        
        return ok(message="CV data structured successfully", data=response)

    except Exception as e:
        return internal_server_error(str(e))


@app.route('/api/v1/hr/candidate/recommend', methods=['POST'])
def recommend_candidates_from_job():
    try:
        data = request.get_json()
        job_data = data.get("job")
        if not job_data:
            return bad_request_error("job is required")

        try:
            validated_job_data = JobData(**job_data)
        except ValidationError as ve:
            error_messages = []
            for error in ve.errors():
                error_messages.append(f"{error['loc'][0]}: {error['msg']}")
            return bad_request_error(f"Invalid job data: {', '.join(error_messages)}")

        job_dict = validated_job_data.model_dump()
        results = asyncio.run(candidate_recommendation.recommend(job_detail=job_dict))
        
        return ok(
            message="Candidate recommendations generated successfully",
            data=results
        )

    except Exception as e:
        app.logger.exception("Error in recommend_candidates_from_job route")
        return internal_server_error(str(e))
    
@app.route('/api/v1/hr/candidate/insert', methods=['POST'])
def insert_candidate():
    try:
        data = request.get_json()
        candidate_data = data.get("candidate")
        if not candidate_data:
            return bad_request_error("candidate is required")

        try:
            validated_candidate = CandidateData(**candidate_data)
        except ValidationError as ve:
            error_messages = []
            for error in ve.errors():
                error_messages.append(f"{error['loc'][0]}: {error['msg']}")
            return bad_request_error(f"Invalid candidate data: {', '.join(error_messages)}")

        candidate_dict = validated_candidate.model_dump()
        
        result = asyncio.run(candidate_recommendation.indexing(candidate_data=candidate_dict))

        return ok(
            message="Candidate indexed successfully",
            data=result
        )

    except Exception as e:
        app.logger.exception("Error in insert_candidate route")
        return internal_server_error(str(e))

@app.route('/api/v1/hr/candidate/<candidate_id>', methods=['GET', 'PUT'])
def handle_candidate(candidate_id):
    if request.method == 'GET':
        try:
            if not candidate_id:
                return bad_request_error("candidate_id is required")

            result = asyncio.run(candidate_service.get_candidate(candidate_id))
            
            if not result:
                return bad_request_error(f"Candidate with ID {candidate_id} not found")

            return ok(
                message="Candidate retrieved successfully",
                data=result.model_dump()
            )

        except Exception as e:
            app.logger.exception("Error in get_candidate route")
            return internal_server_error(str(e))
            
    elif request.method == 'PUT':
        try:
            if not candidate_id:
                return bad_request_error("candidate_id is required")
                
            data = request.get_json()
            if not data:
                return bad_request_error("Request body is required")
            
            result = asyncio.run(candidate_service.update_candidate(candidate_id, data))
            
            if not result:
                return bad_request_error(f"Candidate with ID {candidate_id} not found or update failed")

            return ok(
                message="Candidate updated successfully",
                data=result.model_dump()
            )

        except Exception as e:
            app.logger.exception("Error in update_candidate route")
            return internal_server_error(str(e))

@app.route('/api/v1/hr/candidates', methods=['GET'])
def list_candidates():
    try:
        limit = request.args.get('limit', default=100, type=int)
        
        result = asyncio.run(candidate_service.list_candidates(limit=limit))

        return ok(
            message="Candidates retrieved successfully",
            data=[c.model_dump() for c in result]
        )

    except Exception as e:
        app.logger.exception("Error in list_candidates route")
        return internal_server_error(str(e))

@app.route('/api/v1/hr/candidates/by-status', methods=['GET'])
def get_candidates_by_status():
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', default=100, type=int)
        
        if not status:
            return bad_request_error("status query parameter is required")

        result = asyncio.run(candidate_service.get_candidates_by_status(status=status, limit=limit))

        return ok(
            message=f"Candidates with status '{status}' retrieved successfully",
            data=[c.model_dump() for c in result]
        )

    except Exception as e:
        app.logger.exception("Error in get_candidates_by_status route")
        return internal_server_error(str(e))

@app.route('/api/v1/hr/candidates/by-position', methods=['GET'])
def get_candidates_by_position():
    try:
        position = request.args.get('position')
        limit = request.args.get('limit', default=100, type=int)
        
        if not position:
            return bad_request_error("position query parameter is required")

        result = asyncio.run(candidate_service.get_candidates_by_position(position=position, limit=limit))

        return ok(
            message=f"Candidates for position '{position}' retrieved successfully",
            data=[c.model_dump() for c in result]
        )

    except Exception as e:
        app.logger.exception("Error in get_candidates_by_position route")
        return internal_server_error(str(e))

@app.route('/api/v1/document/analyze', methods=['POST'])
def analyze_document():
    try:
        if 'document' not in request.files:
            return bad_request_error("No document file provided")
        
        file = request.files['document']
        
        if file.filename == '':
            return bad_request_error("No file selected")
        
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return bad_request_error(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Save temporary file
        temp_dir = "assets"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            result = asyncio.run(document_analyzer.analyze_document_kk(document_path=temp_path))
            return ok(
                message="Document analyzed successfully",
                data=result.model_dump()
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        app.logger.exception("Error in analyze_document route")
        return internal_server_error(str(e))
    
@app.route('/api/v1/document/classify', methods=['POST'])
def classify_document():
    try:
        data = request.get_json()
        document_text = data.get('document_text')

        if not document_text:
            return bad_request_error("document_text is required")

        result = asyncio.run(document_analyzer.classify_legal_document(document_content=document_text))

        return ok(
            message="Document classified successfully",
            data=result
        )

    except Exception as e:
        app.logger.exception("Error in classify_document route")
        return internal_server_error(str(e))
    
@app.route('/api/v1/document/upload', methods=['POST'])
def document_upload():
    try:
        candidate_id = request.form.get('candidate_id')
        
        if not candidate_id:
            return bad_request_error("candidate_id is required")
        
        if 'document' not in request.files:
            return bad_request_error("No document file provided")
        
        file = request.files['document']
        
        if file.filename == '':
            return bad_request_error("No file selected")
        
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return bad_request_error(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Save temporary file
        temp_dir = "assets"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            # Analyze document
            result: LegalDocumentResponse = asyncio.run(document_analyzer.upload_document(document_path=temp_path, candidate_id=candidate_id))
            
            # Upload to blob storage
            file.seek(0)  # Reset file pointer
            blob_info = blob_storage.upload_file(file=file, candidate_id=candidate_id, original_filename=file.filename)
            
            # Add blob info to response
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            result_dict['url'] = blob_info.get('url', '')
            result_dict['name'] = file.filename
            result_dict['last_updated'] = blob_info.get('uploaded_at', '')
            
            return ok(
                message="Document uploaded successfully",
                data=result_dict
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        app.logger.exception("Error in document_upload route")
        return internal_server_error(str(e))
    
@app.route('/api/v1/document/analyze/offering-letter', methods=['POST'])
def analyze_document_offering_letter():
    try:
        candidate_id = request.form.get('candidate_id')
        if not candidate_id:
            return bad_request_error("candidate_id is required")
        
        if 'document' not in request.files:
            return bad_request_error("No document file provided")
        
        file = request.files['document']
        
        if file.filename == '':
            return bad_request_error("No file selected")
        
        allowed_extensions = {'.pdf'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return bad_request_error(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Save temporary file
        temp_dir = "assets"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            result = asyncio.run(document_analyzer.analyze_offering_letter(document_path=temp_path))

            # Upload to blob storage
            file.seek(0)  # Reset file pointer
            blob_info = blob_storage.upload_file(file=file, candidate_id=candidate_id, original_filename=file.filename)
            
            # Add blob info to response
            result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
            result_dict['url'] = blob_info.get('url', '')
            result_dict['name'] = file.filename
            result_dict['last_updated'] = blob_info.get('uploaded_at', '')

            return ok(
                message="Document analyzed successfully",
                data=result_dict
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        app.logger.exception("Error in analyze_document route")
        return internal_server_error(str(e))
    
@app.route('/api/v1/employees/by-position', methods=['GET'])
def get_employees_by_position():
    try:
        position = request.args.get('position')
        limit = request.args.get('limit', default=100, type=int)
        
        if not position:
            return bad_request_error("position query parameter is required")

        result = asyncio.run(candidate_service.get_candidates_by_position(position=position, limit=limit))

        return ok(
            message=f"Candidates for position '{position}' retrieved successfully",
            data=[c.model_dump() for c in result]
        )

    except Exception as e:
        app.logger.exception("Error in get_candidates_by_position route")
        return internal_server_error(str(e))
    
@app.route('/api/v1/employees', methods=['GET'])
def list_employees():
    try:
        limit = request.args.get('limit', default=100, type=int)
        
        result = asyncio.run(employee_service.list_employees(limit=limit))

        return ok(
            message="Employees retrieved successfully",
            data=[c.model_dump() for c in result]
        )

    except Exception as e:
        app.logger.exception("Error in list_employees route")
        return internal_server_error(str(e))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)