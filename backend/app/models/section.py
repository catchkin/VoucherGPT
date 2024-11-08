from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from .base import Base

class SectionType(enum.Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_OVERVIEW = "company_overview"
    MARKET_ANALYSIS = "market_analysis"
    BUSINESS_MODEL = "business_model"
    FINANCIAL_PLAN = "financial_plan"
    TECHNICAL_DESCRIPTION = "technical_description"
    OTHER = "other"

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(SectionType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    order = Column(Integer, default=0)
    meta_data = Column(JSON)

    # Foreign keys
    document_id = Column(Integer, ForeignKey("documents.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))

    # Relationships
    document = relationship("Document", back_populates="sections")
    company = relationship("Company", back_populates="sections")

    def __repr__(self):
        return f"<Section(title={self.title}, type={self.type.value})>"

    class Config:
        orm_mode = True
