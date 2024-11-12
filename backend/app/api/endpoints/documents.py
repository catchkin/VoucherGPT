from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import traceback

from app.api.deps import get_db, handle_exceptions
from app.crud import crud_document
from app.core.config import settings
from app.models.document import DocumentType
from app.schemas import (
    Document,
    DocumentCreate,
    DocumentUpdate,
    DocumentWithSections
)
from app.services.document_service import document_service

router = APIRouter()

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
@handle_exceptions()
async def create_document(
    document_in: DocumentCreate,
    db: AsyncSession = Depends(get_db)
) -> Document:
    """문서 메타데이터 생성"""
    try:
        document = await crud_document.create(db, obj_in=document_in)
        return document
    except Exception as e:
        print(f"Error creating document: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}"
        )


@router.get("/", response_model=List[Document])
@handle_exceptions()
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company_id: Optional[int] = None,
    document_type: Optional[DocumentType] = None,
    db: AsyncSession = Depends(get_db)
) -> List[Document]:
    """
    문서 목록 조회
    - pagination 지원
    - 회사 ID로 필터링 가능
    - 문서 타입으로 필터링 가능
    """
    if company_id:
        return await crud_document.get_by_company(
            db,
            company_id=company_id,
            skip=skip,
            limit=limit
        )
    if document_type:
        return await crud_document.get_by_type(
            db,
            doc_type=document_type,
            skip=skip,
            limit=limit
        )
    return await crud_document.get_multi(db, skip=skip, limit=limit)

@router.get("/{document_id}", response_model=Document)
@handle_exceptions()
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
) -> Document:
    """특정 문서 조회"""
    document = await crud_document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.get("/{document_id}/full", response_model=DocumentWithSections)
@handle_exceptions()
async def get_document_with_sections(
    document_id: int,
    db: AsyncSession = Depends(get_db)
) -> DocumentWithSections:
    """문서와 관련 섹션 함께 조회"""
    document = await crud_document.get_with_sections(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.post("/upload", response_model=DocumentWithSections)
@handle_exceptions()
async def upload_and_process_document(
    file: UploadFile = File(...),
    company_id: Optional[int] = Form(None),
    document_type: DocumentType = Form(DocumentType.BUSINESS_PLAN),
    db: AsyncSession = Depends(get_db)
) -> DocumentWithSections:
    """
    문서 파일 업로드 및 처리
    - 파일 업로드
    - 텍스트 추출
    - GPT 분석
    - 섹션 생성
    """
    # 파일 크기 검증
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE} bytes"
        )

    return await document_service.create_document_with_sections(
        db=db,
        file=file,
        company_id=company_id,
        document_type=document_type
    )

@router.put("/{document_id}", response_model=Document)
@handle_exceptions()
async def update_document(
    document_id: int,
    document_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db)
) -> Document:
    """문서 정보 수정"""
    document = await crud_document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return await crud_document.update(db, db_obj=document, obj_in=document_in)

@router.delete("/{document_id}", response_model=Document)
@handle_exceptions()
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
) -> Document:
    """문서 삭제"""
    document = await crud_document.remove(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    raise document

@router.post("/template/{template_id}/generate", response_model=DocumentWithSections)
@handle_exceptions()
async def generate_from_template(
    template_id: int,
    company_id: int,
    db: AsyncSession = Depends(get_db)
) -> DocumentWithSections:
    """템플릿 기반 문서 생성"""
    return await document_service.generate_document_from_template(
        db=db,
        template_id=template_id,
        company_id=company_id
    )

@router.post("/analyze", response_model=List[dict])
@handle_exceptions()
async def analyze_document_content(
    content: str,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """문서 내용 분석"""
    return await document_service.analyze_content(content)

@router.get("/{document_id}/download")
@handle_exceptions()
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """문서 파일 다운로드"""
    document = await crud_document.get(db, id=document_id)
    if not document or not document.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or file not found"
        )

    return FileResponse(
        document.file_path,
        media_type=document.mime_type,
        filename=document.file_name
    )
