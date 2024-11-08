from typing import Optional, List
from enum import Enum
from pydantic import Field, field_validator
from .base import BaseSchema, BaseResponseSchema

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
    @field_validator('mime_type')
    def validate_mime_type(cls, v: Optional[str]) -> Optional[str]:
        if v:
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ]
            if v not in allowed_types:
                raise ValueError(f"Unsupported mime type. Allowed types: {allowed_types}")
        return v

class DocumentUpdate(DocumentBase):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[DocumentType] = None
    content: Optional[str] = None
    company_id = Optional[int] = None

class DocumentInDBBase(DocumentBase, BaseResponseSchema):
    """Base schema for Document in DB"""
    pass

class Document(DocumentInDBBase):
    """Schema for returning Document data"""
    pass

class DocumentWithSections(Document):
    """Schema for returning Document with sections"""
    from .section import Section # Avoid circular import
    sections: List['Section'] = []
