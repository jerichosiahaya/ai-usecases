from flask import Blueprint, request, jsonify
from src.models.case import CaseModel
from src.repository.cosmos_db import CosmosDBRepository
from src.repository.service_bus import ServiceBusRepository
from src.config.env import AppConfig
from src.domain.http_response import ok, bad_request_error, internal_server_error, not_found_error
from src.usecase.cases.chat import CaseChatUseCase
from src.repository.llm.llm_service import LLMService
from loguru import logger
import asyncio

# Create blueprint
cases_bp = Blueprint('cases', __name__, url_prefix='/api/v1/cases')


def init_cases_routes(cosmos_db: CosmosDBRepository, service_bus: ServiceBusRepository = None):
    """Initialize case routes with Cosmos DB repository"""
    
    @cases_bp.route('', methods=['POST'])
    def create_case():
        """Create a new fraud case"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('name') or not data.get('description'):
                return bad_request_error("name and description are required")
            
            # Validate and create case model
            case_data = {
                "name": data.get('name'),
                "description": data.get('description'),
                "status": data.get('status', 'pending'),
                "files": data.get('files', []),
                "insights": data.get('insights'),
                "recommendations": data.get('recommendations')
            }
            
            created_case = cosmos_db.create_case(case_data)
            return ok(message="Case created successfully", data=created_case, status_code=201)
        
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            return internal_server_error(f"Failed to create case: {str(e)}")

    @cases_bp.route('', methods=['GET'])
    def get_cases():
        """Get all cases"""
        try:
            cases = cosmos_db.get_all_cases()
            return ok(message="Cases retrieved successfully", data=cases)
        
        except Exception as e:
            logger.error(f"Error retrieving cases: {e}")
            return internal_server_error(f"Failed to retrieve cases: {str(e)}")

    @cases_bp.route('/<case_id>', methods=['GET'])
    def get_case(case_id: str):
        """Get a specific case by ID"""
        try:
            case = cosmos_db.get_case_by_id(case_id)
            return ok(message="Case retrieved successfully", data=case)
        
        except Exception as e:
            logger.error(f"Error retrieving case {case_id}: {e}")
            return not_found_error(f"Case {case_id} not found")

    @cases_bp.route('/<case_id>', methods=['DELETE'])
    def delete_case(case_id: str):
        """Delete a case"""
        try:
            cosmos_db.delete_case(case_id)
            return ok(message="Case deleted successfully", data={"id": case_id})
        
        except Exception as e:
            logger.error(f"Error deleting case {case_id}: {e}")
            return internal_server_error(f"Failed to delete case: {str(e)}")

    @cases_bp.route('/<case_id>', methods=['PUT'])
    def update_case(case_id: str):
        """Update a case"""
        try:
            data = request.get_json()
            updated_case = cosmos_db.update_case(case_id, data)
            return ok(message="Case updated successfully", data=updated_case)
        
        except Exception as e:
            logger.error(f"Error updating case {case_id}: {e}")
            return internal_server_error(f"Failed to update case: {str(e)}")
    
    @cases_bp.route('/<case_id>/analysis', methods=['POST'])
    def start_analysis(case_id: str):
        """Start analysis for a case"""
        try:
            config = AppConfig()
            # Update case status to analyzing
            update_data = {"status": "analyzing"}
            cosmos_db.update_case(case_id, update_data)
            
            # Send message to Service Bus if configured
            if service_bus:
                message_data = {"case_id": case_id, "action": "analyze"}
                service_bus.send_message(config.SERVICE_BUS_QUEUE_NAME, message_data)
            
            return ok(message="Analysis started successfully", data={"case_id": case_id, "status": "analyzing"})
        
        except Exception as e:
            logger.error(f"Error starting analysis for case {case_id}: {e}")
            return internal_server_error(f"Failed to start analysis: {str(e)}")
    
    @cases_bp.route('/<case_id>/notes', methods=['POST'])
    def add_note(case_id: str):
        """Add a note to a case"""
        try:
            data = request.get_json()
            content = data.get('content')
            
            if not content or not isinstance(content, str) or not content.strip():
                return bad_request_error("Note content is required and must be a non-empty string")
            
            note = {
                "id": f"note-{int(__import__('time').time() * 1000)}",
                "content": content.strip(),
                "created_at": __import__('datetime').datetime.utcnow().isoformat()
            }
            
            case = cosmos_db.get_case_by_id(case_id)
            if not case:
                return not_found_error(f"Case {case_id} not found")
            
            if "notes" not in case:
                case["notes"] = []
            
            case["notes"].append(note)
            cosmos_db.update_case(case_id, {"notes": case["notes"]})
            
            return ok(message="Note added successfully", data=note, status_code=201)
        
        except Exception as e:
            logger.error(f"Error adding note to case {case_id}: {e}")
            return internal_server_error(f"Failed to add note: {str(e)}")
    
    @cases_bp.route('/<case_id>/notes/<note_id>', methods=['DELETE'])
    def delete_note(case_id: str, note_id: str):
        """Delete a note from a case"""
        try:
            case = cosmos_db.get_case_by_id(case_id)
            if not case:
                return not_found_error(f"Case {case_id} not found")
            
            if "notes" not in case:
                return not_found_error(f"Note {note_id} not found")
            
            original_count = len(case["notes"])
            case["notes"] = [note for note in case["notes"] if note.get("id") != note_id]
            
            if len(case["notes"]) == original_count:
                return not_found_error(f"Note {note_id} not found")
            
            cosmos_db.update_case(case_id, {"notes": case["notes"]})
            
            return ok(message="Note deleted successfully", data={"id": note_id})
        
        except Exception as e:
            logger.error(f"Error deleting note {note_id} from case {case_id}: {e}")
            return internal_server_error(f"Failed to delete note: {str(e)}")
    
    @cases_bp.route('/<case_id>/chat', methods=['POST'])
    def chat_with_case(case_id: str):
        """Chat with case analyst with case context"""
        try:
            data = request.get_json()
            messages = data.get('messages')
            session_id = data.get('session_id', f'session-{case_id}')
            # Allow case_id to be overridden from request body if provided
            request_case_id = data.get('case_id', case_id)
            
            # Validate required fields
            if not messages or not isinstance(messages, list) or len(messages) == 0:
                return bad_request_error("messages array is required and must not be empty")
            
            # Validate message structure
            for msg in messages:
                if not msg.get('role') or not msg.get('text'):
                    return bad_request_error("Each message must have 'role' and 'text' fields")
            
            # Initialize services
            config = AppConfig
            llm_service = LLMService(config=config)
            
            # Create chat use case with both services
            chat_usecase = CaseChatUseCase(llm_repository=llm_service, cosmos_db=cosmos_db)
            
            # Execute async chat
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                chat_usecase.chat(messages=messages, session_id=session_id, case_id=request_case_id)
            )
            loop.close()
            
            return ok(message="Chat response received successfully", data=response)
        
        except Exception as e:
            logger.error(f"Error in chat for case {case_id}: {e}")
            return internal_server_error(f"Failed to process chat: {str(e)}")
    
    return cases_bp
