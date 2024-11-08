from typing import Optional, Dict, Any
from enum import Enum
from pydantic import Field
from .base import BaseSchema, BaseResponseSchema

class SectionType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_OVERVIEW = "company_overview"
    MARKET_ANALYSIS = "market_analysis"
    BUSINESS_MODEL = "business_model"
    FINANCIAL_PLAN = "financial_plan"
    TECHNICAL_DESCRIPTION = "technical_description"
    OTHER = "other"

class SectionBase(BaseSchema):
    """Base schema for Section"""
    type: SectionType
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    order: int = Field(0, ge=0)
    meta_data: Optional[Dict[str, Any]] = None
    document_id: Optional[int] = None
    company_id: Optional[int] = None

class SectionCreate(SectionBase):
    """Schema for creating a new section"""
    document_id: int
    company_id: int

class SectionUpdate(SectionBase):
    """Schema for updating a section"""
    type: Optional[SectionType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    order: Optional[int] = Field(None, ge=0)
    meta_data: Optional[Dict[str, Any]] = None

class SectionInDBBase(SectionBase, BaseResponseSchema):
    """Base schema for Section in DB"""
    pass

class Section(SectionInDBBase):
    """Schema for running Section data"""
    pass
