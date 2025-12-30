from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
from loguru import logger
import uuid
from src.usecase.content_extraction import ContentExtraction

router = APIRouter(prefix="/api/v1", tags=["content-extraction"])

@router.post("/extract-content")
async def extract_content(
    file: UploadFile = File(...),
    content_extraction_service: ContentExtraction = None
) -> Dict[str, Any]:
    """
    Extract content from an uploaded document
    
    Args:
        file: The document file to analyze
        content_extraction_service: Injected ContentExtraction service
        
    Returns:
        Dictionary containing upload_id, file metadata and analysis results
    """
    try:
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        if not content_extraction_service:
            raise HTTPException(status_code=500, detail="ContentExtraction service not initialized")
        
        logger.info(f"Received request to extract content from file {file.filename} with upload_id {upload_id}")
        
        # Extract content using the usecase
        result = content_extraction_service.extract_content(
            file=file.file,
            upload_id=upload_id,
            original_filename=file.filename
        )
        
        logger.info(f"Successfully extracted content for upload_id {upload_id}")
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")
    
@router.post("/extract-content")
async def extract_content(
    file: UploadFile = File(...),
    content_extraction_service: ContentExtraction = None
) -> Dict[str, Any]:
    """
    Extract content from an uploaded document
    
    Args:
        file: The document file to analyze
        content_extraction_service: Injected ContentExtraction service
        
    Returns:
        Dictionary containing upload_id, file metadata and analysis results
    """
    try:
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())
        
        if not content_extraction_service:
            raise HTTPException(status_code=500, detail="ContentExtraction service not initialized")
        
        logger.info(f"Received request to extract content from file {file.filename} with upload_id {upload_id}")
        
        # Extract content using the usecase
        result = content_extraction_service.extract_content(
            file=file.file,
            upload_id=upload_id,
            original_filename=file.filename
        )
        
        logger.info(f"Successfully extracted content for upload_id {upload_id}")
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    
    Returns:
        Dictionary indicating service health
    """
    return {
        "status": "healthy",
        "service": "ai-tax-management-system"
    }
