from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ARRAY, JSON, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Company(Base):
    """기업 정보 모델"""
    __tablename__ = "companies"

    # 나머지 코드는 그대로 유지
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    business_number = Column(String(20), unique=True, index=True)
    industry = Column(String(100))
    establishment_date = Column(String(10))
    employee_count = Column(Integer)
    annual_revenue = Column(Integer)
    description = Column(Text)
    target_markets = Column(ARRAY(String))
    export_countries = Column(ARRAY(String))
    export_history = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="company")
    sections = relationship("Section", back_populates="company")
    chat_histories = relationship("ChatHistory", back_populates="company")
