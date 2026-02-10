from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List

class Uploads(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    document_id: str = Field(..., alias="documentId", description="Primary key of the uploaded document")
    status: str = Field(..., alias="status", description="Current processing status of the document")
    user_id: str = Field(..., alias="userId", description="ID of the user who uploaded the document")
    created_at: str = Field(..., alias="createdAt", description="ISO timestamp when the document was created")
    updated_at: str = Field(..., alias="updatedAt", description="ISO timestamp when the document was last updated")