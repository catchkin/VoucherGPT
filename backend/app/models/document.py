from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    document_type = Column(String)  # 'reference', 'sample', 'plan'
    content = Column(Text)
    file_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
