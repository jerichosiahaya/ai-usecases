from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
from loguru import logger
import uuid

from src.config.dependencies import ContentExtractionDep

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    content_extraction_service: ContentExtractionDep = None
) -> Dict[str, Any]:
    """
    Upload and process a document file
    
    Args:
        file: The document file to upload and analyze
        content_extraction_service: Injected ContentExtraction service
        
    Returns:
        Dictionary containing upload_id, file metadata, and processing status
    """
    try:
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        logger.info(f"Received file upload: {file.filename} with upload_id {upload_id}")
        
        # Extract content using the injected service
        result = content_extraction_service.extract_content(
            file=file.file,
            upload_id=upload_id,
            original_filename=file.filename
        )
        
        logger.info(f"Successfully processed file upload for upload_id {upload_id}")
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "message": "File uploaded and processing started",
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
