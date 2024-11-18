from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.crud.base import CRUDBase
from app.models import ChatHistory, ChatReference, ChatFeedback
from app.schemas.chat import (
    ChatHistoryCreate, ChatHistoryUpdate,
    ChatReferenceCreate, ChatReferenceUpdate,
    ChatFeedbackCreate, ChatFeedbackUpdate
)

class CRUDChatHistory(CRUDBase[ChatHistory, ChatHistoryCreate, ChatHistoryUpdate]):
    async def get_by_company(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatHistory]:
        """기업별 채팅 이력 조회"""
        query = (
            select(ChatHistory)
            .where(ChatHistory.company_id == company_id)
            .order_by(desc(ChatHistory.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def search_history(
        self,
        db: AsyncSession,
        *,
        query: str,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatHistory]:
        """채팅 이력 검색"""
        conditions = [
            ChatHistory.query.ilike(f"%{query}%") |
            ChatHistory.response.ilike(f"%{query}%")
        ]
        if company_id:
            conditions.append(ChatHistory.company_id == company_id)

        query = (
            select(ChatHistory)
            .where(and_(*conditions))
            .order_by(desc(ChatHistory.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def toggle_bookmark(
        self,
        db: AsyncSession,
        *,
        chat_id: int,
        is_bookmarked: bool
    ) -> Optional[ChatHistory]:
        """북마크 토글"""
        chat = await self.get(db, id=chat_id)
        if chat:
            chat.is_bookmarked = is_bookmarked
            await db.commit()
            await db.refresh(chat)
        return chat


class CRUDChatReference(CRUDBase[ChatReference, ChatReferenceCreate, ChatReferenceUpdate]):
    async def get_by_chat(
        self,
        db: AsyncSession,
        *,
        chat_id: int
    ) -> List[ChatReference]:
        """채팅별 참조 문서 목록 조회"""
        query = (
            select(ChatReference)
            .where(ChatReference.chat_id == chat_id)
            .order_by(desc(ChatReference.relevance_score))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create_many(
        self,
        db: AsyncSession,
        *,
        chat_id: int,
        document_ids: List[int],
        scores: Optional[Dict[int, float]] = None
    ) -> List[ChatReference]:
        """여러 참조 문서 한 번에 생성"""
        references = []
        for doc_id in document_ids:
            reference = ChatReference(
                chat_id=chat_id,
                document_id=doc_id,
                relevance_score=scores.get(doc_id) if scores else None
            )
            db.add(reference)
            references.append(reference)

        await db.commit()
        for ref in references:
            await db.refresh(ref)
        return references


class CRUDChatFeedback(CRUDBase[ChatFeedback, ChatFeedbackCreate, ChatFeedbackUpdate]):
    async def get_by_chat(
        self,
        db: AsyncSession,
        *,
        chat_id: int
    ) -> Optional[ChatFeedback]:
        """채팅별 피드백 조회"""
        query = select(ChatFeedback).where(ChatFeedback.chat_id == chat_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_company_stats(
        self,
        db: AsyncSession,
        *,
        company_id: int
    ) -> Dict[str, Any]:
        """회사별 피드백 통계"""
        query = (
            select(
                func.count(ChatFeedback.id).label('total_count'),
                func.avg(ChatFeedback.rating).label('avg_rating'),
                func.avg(
                    case((ChatFeedback.is_accurate == True, 1.0), else_=0.0)
                ).label('accuracy_rate')
            )
            .join(ChatHistory)
            .where(ChatHistory.company_id == company_id)
        )
        result = await db.execute(query)
        stats = result.mappings().first()

        return {
            "total_count": int(stats['total_count']),
            "average_rating": float(stats['avg_rating']) if stats['avg_rating'] else 0.0,
            "accuracy_rate": float(stats['accuracy_rate']) if stats['accuracy_rate'] else 0.0
        }

    async def update_or_create(
        self,
        db: AsyncSession,
        *,
        chat_id: int,
        feedback_in: ChatFeedbackCreate
    ) -> ChatFeedback:
        """피드백 업데이트 또는 생성"""
        existing = await self.get_by_chat(db, chat_id=chat_id)
        if existing:
            update_data = feedback_in.model_dump(exclude={'chat_id'})
            return await self.update(db, db_obj=existing, obj_in=update_data)
        return await self.create(db, obj_in=feedback_in)


# CRUD 객체 인스턴스 생성
chat_history = CRUDChatHistory(ChatHistory)
chat_reference = CRUDChatReference(ChatReference)
chat_feedback = CRUDChatFeedback(ChatFeedback)
