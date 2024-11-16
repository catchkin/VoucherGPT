from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import Field

from .base import BaseSchema

class SectionType(str, Enum):
    """섹션 유형 Enum"""
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_OVERVIEW = "company_overview"
    MARKET_ANALYSIS = "market_analysis"
    BUSINESS_MODEL = "business_model"
    FINANCIAL_PLAN = "financial_plan"
    TECHNICAL_DESCRIPTION = "technical_description"
    OTHER = "other"

class SectionBase(BaseSchema):
    """섹션 기본 스키마"""
    type: SectionType
    title: str = Field(..., max_length=255)
    content: Optional[str] = None
    order: Optional[int] = Field(default=0, ge=0)
    meta_data: Optional[dict] = Field(default_factory=dict)

class SectionCreate(SectionBase):
    """섹션 생성 스키마"""
    document_id: int
    company_id: int

class SectionUpdate(SectionBase):
    """섹션 수정 스키마"""
    type: Optional[SectionType] = None
    title: Optional[str] = Field(None, max_length=255)

class SectionInDB(SectionBase):
    """섹션 DB 응답 스키마"""
    id: int
    document_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
