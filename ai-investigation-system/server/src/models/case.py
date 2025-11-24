from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CaseStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CaseModel(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    status: CaseStatus = CaseStatus.PENDING
    files: List[str] = []
    insights: Optional[str] = None
    recommendations: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        use_enum_values = True
