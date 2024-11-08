from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.api.deps import get_db, handle_exceptions, validate_file_size, validate_mime_type
from app.crud import crud_document, company, document
from app.core.config import settings
from app.schemas import DocumentCreate, DocumentUpdate, Document, DocumentWithSections

router = APIRouter()

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
@handle_exceptions()
async def create_document(
    document_in: DocumentCreate,
    db: AsyncSession = Depends(get_db)
) -> Document:
    """새로운 문서 생성"""
    return await crud_document.create(db, obj_in=document_in)

@router.post("/upload", response_model=Document)
@handle_exceptions()
async def upload_document(
    file: UploadFile = File(...),
    company_id: int = None,
    db: AsyncSession = Depends(get_db)
) -> Document:
    """문서 파일 업로드"""
    await validate_file_size(file.size)
    await validate_mime_type(file.content_type)

    # 파일 저장
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # 문서 생성
    document_in = DocumentCreate(
        title=file.filename,
        file_path=file_path,
        file_name=file.filename,
        mime_type=file.content_type,
        company_id=company_id
    )
    return await crud_document.create(db, obj_in=document_in)

@router.get("/", response_model=List[Document])
@handle_exceptions()
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    company_id: int = None,
    db: AsyncSession = Depends(get_db)
) -> List[Document]:
    """문서 목록 조회"""
    if company_id:
        return await crud_document.get_by_company(db, company_id=company_id, skip=skip, limit=limit)
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
    """문서를 섹션들과 함께 조회"""
    document = await crud_document.get_with_sections(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

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
