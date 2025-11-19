from flask import Blueprint, request
from werkzeug.utils import secure_filename
from src.repository.blob_storage import BlobStorageRepository
from src.repository.cosmos_db import CosmosDBRepository
from src.domain.http_response import ok, bad_request_error, internal_server_error
from loguru import logger

# Create blueprint
upload_bp = Blueprint('upload', __name__, url_prefix='/api/v1/upload')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv', 'txt', 'doc', 'docx', 'jpg', 'jpeg', 'png'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_upload_routes(blob_storage: BlobStorageRepository, cosmos_db: CosmosDBRepository = None):
    """Initialize upload routes with Blob Storage repository"""
    
    @upload_bp.route('/file/<case_id>', methods=['POST'])
    def upload_file(case_id: str):
        """Upload a file to Blob Storage for a specific case"""
        try:
            # Check if file is in request
            if 'file' not in request.files:
                return bad_request_error("No file provided")
            
            file = request.files['file']
            
            # Check if file is empty
            if file.filename == '':
                return bad_request_error("No file selected")
            
            # Validate file extension
            if not allowed_file(file.filename):
                allowed = ', '.join(ALLOWED_EXTENSIONS)
                return bad_request_error(f"File type not allowed. Allowed types: {allowed}")
            
            # Secure filename
            filename = secure_filename(file.filename)
            
            # Upload file to Blob Storage
            file_info = blob_storage.upload_file(file, case_id, filename)
            
            # Update case in Cosmos DB to include the new file URL
            if cosmos_db:
                try:
                    case = cosmos_db.get_case_by_id(case_id)
                    if 'files' not in case:
                        case['files'] = []
                    
                    # Get file format from extension
                    file_format = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    
                    # Add the file with new schema
                    new_file = {
                        "url": file_info['url'],
                        "name": file_info['url'],
                        "description": "",
                        "format": file_format
                    }
                    case['files'].append(new_file)
                    cosmos_db.update_case(case_id, {"files": case['files']})
                    logger.info(f"Updated case {case_id} with new file: {file_info['url']}")
                except Exception as e:
                    logger.warning(f"Could not update case in Cosmos DB: {e}")
                    # File was uploaded successfully, so we still return success
            
            return ok(message="File uploaded successfully", data=file_info, status_code=201)
        
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return internal_server_error(f"Failed to upload file: {str(e)}")

    @upload_bp.route('/files/<case_id>', methods=['GET'])
    def list_files(case_id: str):
        """List all files for a case"""
        try:
            files = blob_storage.list_files(case_id)
            return ok(message="Files retrieved successfully", data=files)
        
        except Exception as e:
            logger.error(f"Error listing files for case {case_id}: {e}")
            return internal_server_error(f"Failed to retrieve files: {str(e)}")

    @upload_bp.route('/file/<case_id>/<path:blob_name>', methods=['DELETE'])
    def delete_file(case_id: str, blob_name: str):
        """Delete a file from Blob Storage"""
        try:
            # Reconstruct full blob name
            full_blob_name = f"{case_id}/{blob_name}"
            
            blob_storage.delete_file(full_blob_name)
            
            # Update case in Cosmos DB to remove the file URL
            if cosmos_db:
                try:
                    case = cosmos_db.get_case_by_id(case_id)
                    if 'files' in case:
                        # Find and remove the file that matches this blob name
                        case['files'] = [f for f in case['files'] if blob_name not in f.get('name', '')]
                        cosmos_db.update_case(case_id, {"files": case['files']})
                        logger.info(f"Updated case {case_id} after deleting file: {blob_name}")
                except Exception as e:
                    logger.warning(f"Could not update case in Cosmos DB: {e}")
                    # File was deleted successfully, so we still return success
            
            return ok(message="File deleted successfully", data={"blob_name": full_blob_name})
        
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return internal_server_error(f"Failed to delete file: {str(e)}")
    
    return upload_bp
