from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base  # database.py에서 Base 직접 import

class DocumentType(str, enum.Enum):
    """문서 유형 Enum"""
    BUSINESS_PLAN = "business_plan"
    COMPANY_PROFILE = "company_profile"
    PRODUCT_CATALOG = "product_catalog"
    TRAINING_DATA = "training_data"

class Document(Base):
    """문서 모델"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    type = Column(Enum(DocumentType), nullable=False, index=True)
    content = Column(Text)
    file_path = Column(String(512))
    file_name = Column(String(255))
    mime_type = Column(String(100))
    doc_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="documents")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
    chat_references = relationship("ChatReference", back_populates="document")
