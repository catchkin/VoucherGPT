from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base  # database.py에서 Base 직접 import

class ChatHistory(Base):
    """채팅 이력 모델"""
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    is_bookmarked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="chat_histories")
    references = relationship("ChatReference", back_populates="chat_history", cascade="all, delete-orphan")
    feedback = relationship("ChatFeedback", back_populates="chat_history", uselist=False)

class ChatReference(Base):
    """채팅-문서 참조 관계 모델"""
    __tablename__ = "chat_references"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat_histories.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    is_auto_referenced = Column(Boolean, default=True)
    relevance_score = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="references")
    document = relationship("Document", back_populates="chat_references")

class ChatFeedback(Base):
    """채팅 피드백 모델"""
    __tablename__ = "chat_feedbacks"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat_histories.id", ondelete="CASCADE"), nullable=False, unique=True)
    rating = Column(Integer)
    comment = Column(Text)
    is_accurate = Column(Boolean)
    needs_improvement = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="feedback")
