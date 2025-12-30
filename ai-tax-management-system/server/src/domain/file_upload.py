from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any, Dict

class FileUploadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    activity_id: str = Field(..., description="Activity ID associated with the upload")
    file_name: str = Field(..., description="Original name of the uploaded file")
    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    content_type: str = Field(..., description="MIME type of the uploaded file")
    status: str = Field(..., description="Processing status of the uploaded file")