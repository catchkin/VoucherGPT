from datetime import datetime
from typing import Optional, List
from pydantic import Field, confloat

from .base import BaseSchema

class ChatHistoryBase(BaseSchema):
    """채팅 이력 기본 스키마"""
    query: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    is_bookmarked: Optional[bool] = False

class ChatHistoryCreate(ChatHistoryBase):
    """채팅 이력 생성 스키마"""
    company_id: int

class ChatHistoryUpdate(ChatHistoryBase):
    """채팅 이력 수정 스키마"""
    query: Optional[str] = Field(None, min_length=1)
    response: Optional[str] = Field(None, min_length=1)
    is_bookmarked: Optional[bool] = None

class ChatHistoryInDB(ChatHistoryBase):
    """채팅 이력 DB 응답 스키마"""
    id: int
    company_id: int
    created_at: datetime

class ChatReferenceBase(BaseSchema):
    """채팅 참조 기본 스키마"""
    is_auto_referenced: bool = True
    relevance_score: Optional[confloat(ge=0, le=1)] = Field(None, description="관련성 점수 (0-1)")

class ChatReferenceCreate(ChatReferenceBase):
    """채팅 참조 생성 스키마"""
    chat_id: int
    document_id: int

class ChatReferenceUpdate(ChatReferenceBase):
    """채팅 참조 수정 스키마"""
    is_auto_referenced: Optional[bool] = None
    relevance_score: Optional[confloat(ge=0, le=1)] = None

class ChatReferenceInDB(ChatReferenceBase):
    """채팅 참조 DB 응답 스키마"""
    id: int
    chat_id: int
    document_id: int
    created_at: datetime

class ChatFeedbackBase(BaseSchema):
    """채팅 피드백 기본 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    is_accurate: Optional[bool] = None
    needs_improvement: Optional[str] = None

class ChatFeedbackCreate(ChatFeedbackBase):
    """채팅 피드백 생성 스키마"""
    chat_id: int

class ChatFeedbackUpdate(ChatFeedbackBase):
    """채팅 피드백 수정 스키마"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    is_accurate: Optional[bool] = None
    needs_improvement: Optional[str] = None

class ChatFeedbackInDB(ChatFeedbackBase):
    """채팅 피드백 DB 응답 스키마"""
    id: int
    chat_id: int
    created_at: datetime
