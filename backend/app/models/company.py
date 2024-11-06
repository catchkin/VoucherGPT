from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    business_number = Column(String(20))
    company_info = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business_plans = relationship("BusinessPlan", back_populates="company")
