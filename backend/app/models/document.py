from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base

class DocumentType(str, enum.Enum):  # str 상속 추가
    BUSINESS_PLAN = "business_plan"
    COMPANY_PROFILE = "company_profile"
    FINANCIAL_REPORT = "financial_report"
    TRAINING_DATA = "training_data"
    OTHER = "other"

    @classmethod
    def _missing_(cls, value):
        # 대소문자 구분 없이 매칭
        for member in cls:
            if member.value == value.lower():
                return member
        return None

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    type = Column(
        Enum(DocumentType, name="documenttype", create_constraint=True, validate_strings=True),
        nullable=False
    )
    content = Column(Text)
    file_path = Column(String(512))
    file_name = Column(String(255))
    mime_type = Column(String(100))

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"))

    # Relationships
    company = relationship("Company", back_populates="documents")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(title={self.title}, type={self.type.value})>"
