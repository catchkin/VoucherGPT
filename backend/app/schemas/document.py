from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import Field

from .base import BaseSchema

class DocumentType(str, Enum):
    """문서 유형 Enum"""
    BUSINESS_PLAN = "business_plan"
    COMPANY_PROFILE = "company_profile"
    PRODUCT_CATALOG = "product_catalog"
    TRAINING_DATA = "training_data"

class DocumentBase(BaseSchema):
    """문서 기본 스키마"""
    title: str = Field(..., max_length=255)
    type: DocumentType
    content: Optional[str] = None
    file_name: Optional[str] = Field(None, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    doc_metadata: Optional[dict] = Field(default_factory=dict)

class DocumentCreate(DocumentBase):
    """문서 생성 스키마"""
    company_id: int = Field(..., description="회사 ID")

class DocumentUpdate(DocumentBase):
    """문서 수정 스키마"""
    title: Optional[str] = Field(None, max_length=255)
    type: Optional[DocumentType] = None

class DocumentInDB(DocumentBase):
    """문서 DB 응답 스키마"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime