from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any, Dict

class Education(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    institution: str
    degree: str
    field_of_study: str = Field(..., alias="fieldOfStudy")
    graduation_year: int = Field(..., alias="graduationYear")
    gpa: Optional[float] = None

class WorkExperience(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    company: str
    position: str
    start_date: str = Field(..., alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    is_current: bool = Field(False, alias="isCurrent")
    description: Optional[str] = None

class BoundingBoxDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    content: Optional[str] = None
    page_number: Optional[int] = Field(None, alias="pageNumber")
    polygons: Optional[List[int]] = None

class ExtractedContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bounding_boxes: Optional[List[Dict[str, Any]]] = Field(None, alias="boundingBoxes")
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = Field(None, alias="structuredData")

class Address(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    detail: str
    city: str
    country: str
    zip: Optional[int] = None

class LegalDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    type: str  # RESUME, KTP, KARTU_KELUARGA, IJAZAH, etc.
    name: str
    url: str
    last_updated: str = Field(..., alias="lastUpdated")
    extracted_content: Optional[ExtractedContent] = Field(None, alias="extractedContent")

class BriefData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    occupation: Optional[str] = None
    contact: Optional[str] = None


class FamilyMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str
    relationship: str
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    brief_data: Optional[BriefData] = Field(None, alias="briefData")

class SourceTargetDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    type: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None

class Discrepancy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    category: Optional[str] = None
    field: Optional[str] = None
    severity: Optional[str] = None  # 'low', 'medium', 'high'
    note: Optional[str] = None
    source: Optional[SourceTargetDocument] = None
    target: Optional[SourceTargetDocument] = None

class ListDiscrepancyResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    discrepancies: List[Discrepancy]

class Employee(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both snake_case and camelCase
        from_attributes=True
    )
    
    id: str
    employee_id: str = Field(..., alias="employeeId")
    name: str
    
    @field_validator('discrepancies', mode='before')
    @classmethod
    def normalize_discrepancies(cls, v):
        """Normalize discrepancies to always be a list."""
        if v is None:
            return None
        if isinstance(v, dict):
            # Convert single dict to list containing that dict
            return [v]
        if isinstance(v, list):
            return v
        return v
    photo_url: Optional[str] = Field(None, alias="photoUrl")
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    address: Optional[Address] = None
    position: Optional[str] = None
    status: Optional[str] = None
    joined_date: Optional[str] = Field(None, alias="joinedDate")
    experience: Optional[float] = None
    legal_documents: Optional[List[LegalDocument]] = Field(None, alias="legalDocuments")
    education: Optional[List[Education]] = None
    work_experiences: Optional[List[WorkExperience]] = Field(None, alias="workExperiences")
    family_members: Optional[List[FamilyMember]] = Field(None, alias="familyMembers")
    resume: Optional[Dict[str, Any]] = None
    discrepancies: Optional[List[Discrepancy]] = None
    embeddings: Optional[List[float]] = None