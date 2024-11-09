from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import Field, model_validator, ConfigDict
from .base import BaseSchema, BaseResponseSchema

if TYPE_CHECKING:
    from .document import Document

class CompanyBase(BaseSchema):
    """Base schema for Company"""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    business_number: Optional[str] = Field(None, max_length=20, description="Business registration number")
    industry: Optional[str] = Field(None, max_length=100)
    establishment_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[int] = Field(None, ge=0, description="Annual revenue in millions")
    description: Optional[str] = None
    is_active: bool = True

class CompanyCreate(CompanyBase):
    """Schema for creating a new company"""
    @model_validator(mode='after')
    def validate_establishment_date(self) -> 'CompanyCreate':
        if self.establishment_date:
            try:
                datetime.strptime(self.establishment_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("establishment_date must be in YYYY-MM-DD format")
        return self

class CompanyUpdate(CompanyBase):
    """Schema for updating a company"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class Company(CompanyBase, BaseResponseSchema):
    """Schema for returning Company data"""
    model_config = ConfigDict(from_attributes=True)

class CompanyWithRelations(Company):
    """Schema for returning Company with related data"""
    documents: List["Document"] = Field(default_factory=list)

from .document import Document
CompanyWithRelations.model_rebuild()