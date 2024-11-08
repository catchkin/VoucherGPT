from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    template_id = Column(Integer, ForeignKey("templates.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    # 관계 설정
    company = relationship("Company", back_populates="documents")
    template = relationship("Template", back_populates="documents")
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")
