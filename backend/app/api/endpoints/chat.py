from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas import ChatFeedbackUpdate
from app.schemas.chat import (
    ChatHistoryCreate, ChatHistoryInDB,
    ChatReferenceCreate, ChatReferenceInDB,
    ChatFeedbackCreate, ChatFeedbackInDB
)
from app.crud.chat import chat_history, chat_reference, chat_feedback


router = APIRouter()

# 채팅 이력 관련 엔드포인트
@router.post("/history", response_model=ChatHistoryInDB)
@deps.handle_exceptions()
async def create_chat(
    chat_in: ChatHistoryCreate,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """새로운 채팅 생성"""
    # 회사 존재 여부 확인
    await deps.validate_company(chat_in.company_id, db)
    return await chat_history.create(db, obj_in=chat_in)

@router.get("/history/company/{company_id}", response_model=List[ChatHistoryInDB])
@deps.handle_exceptions()
async def get_company_chats(
    company_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """회사별 채팅 이력 조회"""
    await deps.validate_company(company_id, db)
    return await chat_history.get_by_company(
        db,
        company_id=company_id,
        skip=commons.skip,
        limit=commons.limit
    )

@router.get("/history/{chat_id}", response_model=ChatHistoryInDB)
@deps.handle_exceptions()
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """특정 채팅 조회"""
    chat = await chat_history.get(db, id=chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history not found"
        )
    return chat

@router.put("/history/{chat_id}/bookmark")
@deps.handle_exceptions()
async def toggle_bookmark(
    chat_id: int,
    is_bookmarked: bool,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """채팅 북마크 토글"""
    updated_chat = await chat_history.toggle_bookmark(
        db,
        chat_id=chat_id,
        is_bookmarked=is_bookmarked
    )
    if not updated_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history not found"
        )
    return {"status": "success"}

@router.delete("/history/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
@deps.handle_exceptions()
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """채팅 삭제"""
    result = await chat_history.remove(db, id=chat_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history not found"
        )

# 채팅 참조 관련 엔드포인트
@router.post("/references", response_model=List[ChatReferenceInDB])
@deps.handle_exceptions()
async def create_references(
    chat_id: int,
    document_ids: List[int],
    scores: Optional[Dict[int, float]] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """채팅 참조 문서 추가"""
    return await chat_reference.create_many(
        db,
        chat_id=chat_id,
        document_ids=document_ids,
        scores=scores
    )

@router.get("/references/{chat_id}", response_model=List[ChatReferenceInDB])
@deps.handle_exceptions()
async def get_chat_references(
    chat_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """채팅의 참조 문서 목록 조회"""
    return await chat_reference.get_by_chat(db, chat_id=chat_id)

# 피드백 관련 엔드포인트
@router.post("/feedback", response_model=ChatFeedbackInDB)
@deps.handle_exceptions()
async def create_feedback(
    feedback_in: ChatFeedbackCreate,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """피드백 생성 또는 업데이트"""
    return await chat_feedback.update_or_create(
        db,
        chat_id=feedback_in.chat_id,
        feedback_in=feedback_in
    )

@router.get("/feedback/{chat_id}", response_model=ChatFeedbackInDB)
@deps.handle_exceptions()
async def get_feedback(
    chat_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """특정 채팅의 피드백 조회"""
    feedback = await chat_feedback.get_by_chat(db, chat_id=chat_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback

@router.get("/feedback/stats/company/{company_id}")
@deps.handle_exceptions()
async def get_company_feedback_stats(
    company_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """회사별 피드백 통계 조회"""
    await deps.validate_company(company_id, db)
    return await chat_feedback.get_company_stats(db, company_id=company_id)

# 통합 검색 엔드포인트
@router.get("/search", response_model=List[ChatHistoryInDB])
@deps.handle_exceptions()
async def search_chats(
    query: str,
    company_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """채팅 이력 검색"""
    if company_id:
        await deps.validate_company(company_id, db)
    return await chat_history.search_history(
        db,
        query=query,
        company_id=company_id,
        skip=commons.skip,
        limit=commons.limit
    )

