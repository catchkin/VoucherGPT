from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from enum import Enum

from .base import Base

class DocumentType(str, Enum):
    BUSINESS_PLAN = "BUSINESS_PLAN"
    COMPANY_PROFILE = "COMPANY_PROFILE"
    PRODUCT_CATALOG = "PRODUCT_CATALOG"
    MARKETING_REPORT = "MARKETING_REPORT"
    MARKET_RESEARCH = "MARKET_RESEARCH"
    TRAINING_DATA = "TRAINING_DATA"
    EXPORT_HISTORY = "EXPORT_HISTORY"
    CHECKLIST = "CHECKLIST"
    OTHER = "OTHER"

class Document(Base):
    __tablename__ = "documents"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    content = Column(Text)
    file_path = Column(String(512))
    file_name = Column(String(255))
    mime_type = Column(String(100))
    metadata = Column(JSONB)

    # Relationships
    company = relationship("Company", back_populates="documents")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
    chat_references = relationship("ChatReference", back_populates="document")

    def __repr__(self):
        return f"<Document(title={self.title}, type={self.document_type})>"
