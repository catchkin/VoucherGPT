from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatHistory, ChatReference, ChatFeedback
from app.schemas.chat import (
    ChatHistoryCreate, ChatReferenceCreate, ChatFeedbackCreate,
    ChatHistoryUpdate, ChatReferenceUpdate, ChatFeedbackUpdate
)
from .base import CRUDBase

class CRUDChatHistory(CRUDBase[ChatHistory, ChatHistoryCreate, ChatHistoryUpdate]):
    async def get_by_company(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatHistory]:
        """기업별 채팅 이력 조회"""
        query = select(self.model)\
            .where(self.model.company_id == company_id)\
            .order_by(self.model.created_at.desc())\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_bookmarked(
        self, db: AsyncSession, *, company_id: int
    ) -> List[ChatHistory]:
        """북마크된 채팅 이력 조회"""
        query = select(self.model)\
            .where(
                self.model.company_id == company_id,
                self.model.is_bookmarked == True
            )\
            .order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

class CRUDChatReference(CRUDBase[ChatReference, ChatReferenceCreate, ChatReferenceUpdate]):
    async def get_by_chat(
        self, db: AsyncSession, *, chat_id: int
    ) -> List[ChatReference]:
        """채팅별 참조 문서 조회"""
        query = select(self.model)\
            .where(self.model.chat_id == chat_id)\
            .order_by(self.model.relevance_score.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_document(
        self, db: AsyncSession, *, document_id: int
    ) -> List[ChatReference]:
        """문서별 채팅 참조 조회"""
        query = select(self.model)\
            .where(self.model.document_id == document_id)\
            .order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

class CRUDChatFeedback(CRUDBase[ChatFeedback, ChatFeedbackCreate, ChatFeedbackUpdate]):
    async def get_by_chat(
        self, db: AsyncSession, *, chat_id: int
    ) -> Optional[ChatFeedback]:
        """채팅별 피드백 조회"""
        query = select(self.model).where(self.model.chat_id == chat_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_positive_feedback(
        self, db: AsyncSession, *, min_rating: int = 4
    ) -> List[ChatFeedback]:
        """긍정적인 피드백 조회"""
        query = select(self.model)\
            .where(self.model.rating >= min_rating)\
            .order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

chat_history = CRUDChatHistory(ChatHistory)
chat_reference = CRUDChatReference(ChatReference)
chat_feedback = CRUDChatFeedback(ChatFeedback)
