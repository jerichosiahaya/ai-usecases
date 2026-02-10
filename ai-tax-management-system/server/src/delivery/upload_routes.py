from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Dict, Any, Optional
from loguru import logger
import uuid

from src.config.dependencies import FileUploadDep, GLUploadDep

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/file")
async def upload_file(
    file: UploadFile = File(..., description="The PDF document file to upload and analyze. Only PDF files are accepted."),
    activity_id: Optional[str] = Form(None, description="Activity ID to associate with the upload. If not provided, a new UUID will be generated."),
    file_upload_service: FileUploadDep = None
):
    try:
        # Validate PDF file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
            
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"Only PDF files are accepted. Received: {file.filename}"
            )
        
        # Validate content type (optional but recommended)
        if file.content_type and file.content_type not in ['application/pdf', 'application/x-pdf']:
            logger.warning(
                f"Content type mismatch for {file.filename}: {file.content_type}. "
                "Proceeding based on file extension."
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())

        activity_id = activity_id if activity_id else str(uuid.uuid4())
        
        logger.info(f"Received PDF upload: {file.filename} with file_id {file_id} and activity_id {activity_id}")
        
        # Extract content using the injected service
        result = file_upload_service.upload(
            file=file.file,
            file_id=file_id,
            activity_id=activity_id,
            original_filename=file.filename
        )
        
        logger.info(f"Successfully processed PDF upload for file_id {file_id} and activity_id {activity_id}")
        
        return {
            "status": "success",
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    

@router.get("/list")
async def list_files(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    file_upload_service: FileUploadDep = None
):
    try:
        result = file_upload_service.list_files(status=status, page=page, page_size=page_size)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.post("/file/gl")
def upload_gl_file(
    file: UploadFile = File(..., description="The PDF document file to upload and analyze. Only PDF files are accepted."),
    file_upload_service: GLUploadDep = None
):
    try:

        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
            
        if not file.filename.lower().endswith('.xlsx'):
            raise HTTPException(
                status_code=400, 
                detail=f"Only XLSX files are accepted. Received: {file.filename}"
            )
        
        # Validate content type (optional but recommended)
        if file.content_type and file.content_type not in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/xlsx']:
            logger.warning(
                f"Content type mismatch for {file.filename}: {file.content_type}. "
                "Proceeding based on file extension."
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Extract content using the injected service
        result = file_upload_service.upload(
            file=file.file,
            file_id=file_id,
            original_filename=file.filename
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
