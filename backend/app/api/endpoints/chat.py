from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.deps import get_db, handle_exceptions
from app.services.chat_service import chat_service
from app.crud import crud_company, crud_document
from app.models.document import DocumentType
from app.schemas.chat import (
    ChatResponse,
    ChatRequest,
    ChatHistory,
    ChatFeedback,
    DocumentReference
)

router = APIRouter()

@router.post("/chat/{company_id}", response_model=ChatResponse)
@handle_exceptions()
async def process_chat(
    company_id: int,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    채팅 메시지 처리 및 응답 생성
    """
    # 회사 존재 여부 확인
    company = await crud_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    response = await chat_service.generate_response(
        company_id=company_id,
        query=chat_request.query,
        db=db
    )

    # 채팅 이력 저장
    chat_history = await chat_service.save_chat_history(
        db=db,
        company_id=company_id,
        query=chat_request.query,
        response=response,
        context_docs=chat_request.context_documents
    )

    return ChatResponse(
        company_id=company_id,
        query=chat_request.query,
        response=response,
        chat_id=chat_history.id,
        created_at=datetime.utcnow(),
        document_references=await chat_service.get_referenced_documents(db, response)
    )






