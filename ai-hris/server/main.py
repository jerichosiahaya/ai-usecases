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

cv_scoring = CVScoring(llm_service=llm)
cv_extractor = CVExtractor(llm_service=llm)
candidate_recommendation = CandidateRecommendation(cosmosdb=cosmosdb, embedding_service=azembedding)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)