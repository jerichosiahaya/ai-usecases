from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class CosmosDocument(BaseModel):
    """Base model for all Cosmos DB documents"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., description="Unique document identifier")
    type: str = Field(..., description="Document type for filtering")
    created_at: str = Field(..., description="ISO timestamp when document was created")
    updated_at: str = Field(..., description="ISO timestamp when document was last updated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "document",
                "created_at": "2025-12-16T12:00:00.000Z",
                "updated_at": "2025-12-16T12:00:00.000Z"
            }
        }


class FileMetadata(BaseModel):
    """Metadata for uploaded files"""
    model_config = ConfigDict(populate_by_name=True)
    
    url: Optional[str] = Field(None, description="File URL or storage path")
    name: Optional[str] = Field(None, description="File name")
    description: Optional[str] = Field("", description="File description")
    classification: Optional[str] = Field("", description="File classification")
    format: Optional[str] = Field(None, description="File format/extension")
    size: Optional[int] = Field(None, description="File size in bytes")


class UploadedFileInfo(BaseModel):
    """Information about an individual uploaded file"""
    model_config = ConfigDict(populate_by_name=True)
    
    filename: str = Field(..., description="Name of the uploaded file")
    size: int = Field(..., description="File size in bytes")
    object_name: str = Field(..., description="Storage object name/path")
    page: Optional[int] = Field(None, description="Page number if part of multi-page PDF")


class UploadDocument(CosmosDocument):
    """Domain model for file upload tracking in Cosmos DB"""
    
    activity_id: str = Field(..., description="Activity ID grouping related uploads")
    original_filename: str = Field(..., description="Original uploaded filename")
    total_size: int = Field(..., description="Total size of all uploaded files in bytes")
    total_pages: int = Field(default=1, description="Total number of pages/files")
    is_multi_page: bool = Field(default=False, description="Whether this is a multi-page document")
    files: List[UploadedFileInfo] = Field(default_factory=list, description="List of uploaded file information")
    status: str = Field(default="uploaded", description="Upload status")
    processing_status: str = Field(default="pending", description="Processing status")
    uploaded_at: str = Field(..., description="ISO timestamp when files were uploaded")
    processed_at: Optional[str] = Field(None, description="ISO timestamp when processing completed")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "file-123",
                "type": "upload",
                "activity_id": "activity-456",
                "original_filename": "document.pdf",
                "total_size": 12345,
                "total_pages": 3,
                "is_multi_page": True,
                "files": [],
                "status": "uploaded",
                "processing_status": "pending",
                "uploaded_at": "2025-12-16T12:00:00.000Z",
                "created_at": "2025-12-16T12:00:00.000Z",
                "updated_at": "2025-12-16T12:00:00.000Z"
            }
        }


class CaseDocument(CosmosDocument):
    """Domain model for case documents in Cosmos DB"""
    
    name: Optional[str] = Field(None, description="Case name")
    description: Optional[str] = Field(None, description="Case description")
    status: str = Field(default="pending", description="Case status")
    files: List[FileMetadata] = Field(default_factory=list, description="List of associated files")
    case_main_category: Optional[str] = Field(None, description="Main category of the case")
    case_sub_category: Optional[str] = Field(None, description="Sub-category of the case")
    analysis: Optional[str] = Field(None, description="Case analysis")
    applicable_laws: List[str] = Field(default_factory=list, description="List of applicable laws")
    law_impact_analysis: Optional[str] = Field("", description="Legal impact analysis")
    insights: Optional[str] = Field(None, description="Case insights")
    recommendations: Optional[str] = Field(None, description="Recommendations")
    caseId: Optional[str] = Field(None, description="Duplicate ID for partition key compatibility")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "case",
                "name": "Tax Case 2025",
                "description": "Tax compliance review",
                "status": "pending",
                "files": [],
                "created_at": "2025-12-16T12:00:00.000Z",
                "updated_at": "2025-12-16T12:00:00.000Z"
            }
        }

class TaxInvoice(BaseModel):
    """Model for tax invoice details"""
    model_config = ConfigDict(populate_by_name=True)
    
    tax_invoice_id: str = Field(..., description="Unique tax invoice identifier")
