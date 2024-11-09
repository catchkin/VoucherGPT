from typing import Optional, List, TYPE_CHECKING, Annotated
from enum import Enum
from pydantic import Field, ConfigDict
from .base import BaseSchema, BaseResponseSchema

if TYPE_CHECKING:
    from .section import Section

class DocumentType(str, Enum):
    BUSINESS_PLAN = "business_plan"
    COMPANY_PROFILE = "company_profile"
    FINANCIAL_REPORT = "financial_report"
    TRAINING_DATA = "training_data"
    OTHER = "other"

class DocumentBase(BaseSchema):
    """Base schema for Document"""
    title: str = Field(..., min_length=1, max_length=255)
    type: DocumentType
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=512)
    file_name: Optional[str] = Field(None, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    company_id: Optional[int] = None

class DocumentCreate(DocumentBase):
    """Schema for creating a new document"""
    pass

class DocumentUpdate(DocumentBase):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[DocumentType] = None
    content: Optional[str] = None
    company_id: Optional[int] = None

class Document(DocumentBase, BaseResponseSchema):
    """Schema for returning Document data"""
    model_config = ConfigDict(from_attributes=True)

class DocumentWithSections(Document):
    """Schema for returning Document with related data"""
    sections: List["Section"] = Field(default_factory=list)

from .section import Section
DocumentWithSections.model_rebuild()