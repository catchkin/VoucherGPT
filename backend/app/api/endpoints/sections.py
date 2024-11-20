from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.section import SectionType
from app.schemas.section import (
    SectionCreate,
    SectionUpdate,
    SectionInDB
)
from app.crud.section import section

router = APIRouter()

@router.post("/", response_model=SectionInDB, status_code=status.HTTP_201_CREATED)
@deps.handle_exceptions()
async def create_section(
    section_in: SectionCreate,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """새로운 섹션 생성"""
    # 문서 존재 여부 확인
    await deps.validate_document(section_in.document_id, db)

    # 회사 존재 여부 확인
    await deps.validate_company(section_in.company_id, db)

    return await section.create_with_order(db=db, obj_in=section_in)

@router.get("/{section_id}", response_model=SectionInDB)
@deps.handle_exceptions()
async def get_section(
    section_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """특정 섹션 조회"""
    db_section = await section.get(db, id=section_id)
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return db_section

@router.put("/{section_id}", response_model=SectionInDB)
@deps.handle_exceptions()
async def update_section(
    section_id: int,
    section_in: SectionUpdate,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """섹션 정보 수정"""
    db_section = await section.get(db, id=section_id)
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return await section.update(db, db_obj=db_section, obj_in=section_in)

@router.delete("/{section_id}",  status_code=status.HTTP_204_NO_CONTENT)
@deps.handle_exceptions()
async def delete_section(
    section_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """섹션 삭제"""
    db_section = await section.get(db, id=section_id)
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    await section.remove(db, id=section_id)

@router.get("/document/{document_id}", response_model=List[SectionInDB])
@deps.handle_exceptions()
async def get_document_sections(
    document_id: int,
    section_type: Optional[SectionType] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """문서의 섹션 목록 조회"""
    await deps.validate_document(document_id, db)

    if section_type:
        return await section.get_by_type(
            db,
            section_type=section_type,
            document_id=document_id,
            skip=commons.skip,
            limit=commons.limit
        )
    return await section.get_by_document(
        db,
        document_id=document_id,
        skip=commons.skip,
        limit=commons.limit
    )

@router.get("/types/", response_model=List[SectionInDB])
@deps.handle_exceptions()
async def get_sections_by_type(
    section_type: SectionType,
    document_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """섹션 유형별 조회"""
    if document_id:
        await deps.validate_document(document_id, db)

    return await section.get_by_type(
        db,
        section_type=section_type,
        document_id=document_id,
        skip=commons.skip,
        limit=commons.limit
    )

