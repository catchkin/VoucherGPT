from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base  # database.py에서 Base 직접 import

class SectionType(str, enum.Enum):
    """섹션 유형 Enum"""
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_OVERVIEW = "company_overview"
    MARKET_ANALYSIS = "market_analysis"
    BUSINESS_MODEL = "business_model"
    FINANCIAL_PLAN = "financial_plan"
    TECHNICAL_DESCRIPTION = "technical_description"
    OTHER = "other"

class Section(Base):
    """문서 섹션 모델"""
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(SectionType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    order = Column(Integer, default=0)
    meta_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="sections")
    company = relationship("Company", back_populates="sections")
