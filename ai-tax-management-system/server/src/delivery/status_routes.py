from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from loguru import logger
from src.domain.http_response import Response
from src.config.dependencies import FileUploadDep

router = APIRouter(prefix="/api/v1/status", tags=["status"])


@router.get("/{document_id}")
async def check_status(
    document_id: str,
    file_upload_service: FileUploadDep = None
) -> Dict[str, Any]:
    try:
        logger.info(f"Checking status for document_id: {document_id}")
        
        result = file_upload_service.get_status(document_id=document_id)
        
        # Placeholder response
        response_content = Response(
            status="success",
            message="Status retrieved successfully",
            data={
                "document_id": document_id,
                "processing_status": "pending"
            }
        )
        return JSONResponse(content=response_content.model_dump(), status_code=200)
    
    except Exception as e:
        logger.error(f"Error checking status for document_id {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")
