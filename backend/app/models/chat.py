from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

class ChatHistory(Base):
    """채팅 이력"""
    __tablename__ = "chat_histories"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    is_bookmarked = Column(Boolean, default=False)

    # Relationships
    company = relationship("Company", back_populates="chat_histories")
    references = relationship("ChatReference", back_populates="chat_history", cascade="all, delete-orphan")
    feedback = relationship("ChatFeedback", back_populates="chat_history", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, company_id={self.company_id})>"

class ChatReference(Base):
    """채팅 참조 문서"""
    __tablename__ = "chat_references"

    chat_id = Column(Integer, ForeignKey("chat_histories.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    is_auto_referenced = Column(Boolean, default=False)
    relevance_score = Column(Float)

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="references")
    document = relationship("Document", back_populates="chat_references")

    def __repr__(self):
        return f"<ChatReference(chat_id={self.chat_id}, document_id={self.document_id})>"

class ChatFeedback(Base):
    """채팅 피드백"""
    __tablename__ = "chat_feedbacks"

    chat_id = Column(Integer, ForeignKey("chat_histories.id"), nullable=False, unique=True)
    rating = Column(Integer, CheckConstraint("rating >= 1 AND rating <= 5"))
    comment = Column(Text)
    is_accurate = Column(Boolean)
    needs_improvement = Column(Text)

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="feedback")

    def __repr__(self):
        return f"<ChatFeedback(chat_id={self.chat_id}, rating={self.rating})>"
