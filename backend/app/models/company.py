from sqlalchemy import Column, String, Integer, Text, Boolean, ARRAY, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base

class Company(Base):
    __tablename__ = "companies"

    name = Column(String(255), nullable=False, index=True)
    business_number = Column(String(20), index=True, unique=True)
    industry = Column(String(100))
    establishment_date = Column(String(10))
    employee_count = Column(Integer)
    annual_revenue = Column(Integer)
    description = Column(Text)
    is_active = Column(Boolean)
    target_markets = Column(ARRAY(String))
    export_countries = Column(ARRAY(String))
    product_categories = Column(String)
    yearly_export_amount = Column(Integer)
    export_history = Column(JSON)

    # Relationships
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="company", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(name={self.name}, business_number={self.business_number})>"
