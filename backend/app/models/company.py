from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    business_number = Column(String(20), unique=True, index=True)
    industry = Column(String(100))
    establishment_date = Column(String(10))
    employee_count = Column(Integer)
    annual_revenue = Column(Integer)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    # Relationships
    documents = relationship("Document", back_populates="company")
    sections = relationship("Section", back_populates="company")

    def __repr__(self):
        return f"<Company(name={self.name}, business_number={self.business_number})>"