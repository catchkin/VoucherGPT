from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class BusinessPlan(Base):
    __tablename__ = "business_plans"

    id = Column(Integer, primary_key=True, index=True)
    company_data = Column(JSON)
    content = Column(JSON)
    status = Column(String) # 'draft', 'completed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
