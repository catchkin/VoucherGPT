from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, constr

from .base import BaseSchema

class CompanyBase(BaseSchema):
    """기업 정보 기본 스키마"""
    name: str = Field(..., max_length=255, description="기업명")
    business_number: str = Field(
        ...,
        pattern=r'^\d{10}$',
        description="사업자등록번호 (10자리)"
    )
    industry: Optional[str] = Field(None, max_length=100, description="산업 분류")
    establishment_date: Optional[str] = Field(
        None,
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="설립일자 (YYYY-MM-DD)"
    )
    employee_count: Optional[int] = Field(None, ge=0, description="임직원 수")
    annual_revenue: Optional[int] = Field(None, ge=0, description="연간 매출액")
    description: Optional[str] = None
    target_markets: Optional[List[str]] = Field(default_factory=list, description="목표 시장")
    export_countries: Optional[List[str]] = Field(default_factory=list, description="수출 국가")
    export_history: Optional[dict] = Field(default_factory=dict, description="수출 이력")


class CompanyCreate(CompanyBase):
    """기업 생성 스키마"""
    pass

class CompanyUpdate(CompanyBase):
    """기업 수정 스키마"""
    name: Optional[str] = Field(None, max_length=255)
    business_number: Optional[str] = Field(None, pattern=r'^\d{10}$')

class CompanyInDB(CompanyBase):
    """기업 DB 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CompanyWithRelations(CompanyInDB):
    """관계 정보를 포함한 기업 응답 스키마"""
    documents: List["DocumentInDB"] = []
    sections: List["SectionInDB"] = []
