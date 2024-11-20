from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.document import DocumentType
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentInDB
)
from app.crud.document import document


router = APIRouter()

@router.post("/", response_model=DocumentInDB, status_code=status.HTTP_201_CREATED)
@deps.handle_exceptions()
async def create_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    type: DocumentType = Form(...),
    company_id: int = Form(...),
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """새로운 문서 생성"""
    # Pydantic 모델로 변환하여 검증
    document_in = DocumentCreate(
        title=title,
        type=type,
        company_id=company_id
    )

    # 회사 존재 여부 확인
    await deps.validate_company(document_in.company_id, db)

    # 파일 타입 검증
    await deps.validate_file_type(file.content_type)

    return await document.create_with_file(db=db, obj_in=document_in, file=file)

@router.get("/{document_id}", response_model=DocumentInDB)
@deps.handle_exceptions()
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """특정 문서 조회"""
    db_document = await document.get(db, id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return db_document

@router.put("/{document_id}", response_model=DocumentInDB)
@deps.handle_exceptions()
async def update_document(
    document_id: int,
    title: str = Form(None),
    type: Optional[DocumentType] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """문서 정보 수정"""
    db_document = await document.get(db, id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # 업데이트 데이터 생성
    update_data = DocumentUpdate(
        title=title if title else db_document.title,
        type=type if type else db_document.type
    )

    # 파일이 제공된 경우 파일 타입 검증
    if file:
        await deps.validate_file_type(file.content_type)

    return await document.update_with_file(
        db=db,
        db_obj=db_document,
        obj_in=update_data,
        file=file
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
@deps.handle_exceptions()
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """문서 삭제"""
    db_document = await document.get(db, id=document_id)
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    await document.remove_with_file(db=db, id=document_id)

@router.get("/company/{company_id}", response_model=List[DocumentInDB])
@deps.handle_exceptions()
async def get_company_documents(
    company_id: int,
    document_type: Optional[DocumentType] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """회사의 문서 목록 조회"""
    await deps.validate_company(company_id, db)

    if document_type:
        return await document.get_by_type(
            db,
            doc_type=document_type,
            company_id=company_id,
            skip=commons.skip,
            limit=commons.limit
        )
    return await document.get_by_company(
        db,
        company_id=company_id,
        skip=commons.skip,
        limit=commons.limit
    )

@router.get("/search/", response_model=List[DocumentInDB])
@deps.handle_exceptions()
async def search_documents(
    query: str,
    company_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """문서 검색"""
    if company_id:
        await deps.validate_company(company_id, db)

    return await document.search_documents(
        db,
        query=query,
        company_id=company_id,
        skip=commons.skip,
        limit=commons.limit
    )

@router.get("/types/", response_model=List[DocumentInDB])
@deps.handle_exceptions()
async def get_documents_by_type(
    document_type: DocumentType,
    company_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """문서 유형별 조회"""
    if company_id:
        await deps.validate_company(company_id, db)

    return await document.get_by_type(
        db,
        doc_type=document_type,
        company_id=company_id,
        skip=commons.skip,
        limit=commons.limit
    )

