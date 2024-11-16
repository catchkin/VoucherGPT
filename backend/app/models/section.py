from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.base import Base

class SectionType(str, Enum):
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
    COMPANY_OVERVIEW = "COMPANY_OVERVIEW"
    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    BUSINESS_MODEL = "BUSINESS_MODEL"
    FINANCIAL_PLAN = "FINANCIAL_PLAN"
    TECHNICAL_DESCRIPTION = "TECHNICAL_DESCRIPTION"
    OTHER = "OTHER"

class Section(Base):
    __tablename__ = "sections"

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type = Column(SQLEnum(SectionType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    order = Column(Integer, default=0)
    meta_data = Column(JSON)

    # Relationships
    document = relationship("Document", back_populates="sections")
    company = relationship("Company", back_populates="sections")

    def __repr__(self):
        return f"<Section(title={self.title}, type={self.type})>"
