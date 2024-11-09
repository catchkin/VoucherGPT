from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, handle_exceptions
from app.crud import crud_section
from app.schemas import SectionCreate, SectionUpdate, Section

router = APIRouter()

@router.post("/", response_model=Section, status_code=status.HTTP_201_CREATED)
@handle_exceptions()
async def create_section(
    section_in: SectionCreate,
    db: AsyncSession = Depends(get_db)
) -> Section:
    """새로운 섹션 생성"""
    return await crud_section.create(db, obj_in=section_in)

@router.get("/document/{document_id}", response_model=List[Section])
@handle_exceptions()
async def list_sections_by_document(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Section]:
    """문서의 섹션 목록 조회"""
    return await crud_section.get_by_document(db, document_id=document_id, skip=skip, limit=limit)

@router.get("/{section_id}", response_model=Section)
@handle_exceptions()
async def get_section(
    section_id: int,
    db: AsyncSession = Depends(get_db)
) -> Section:
    """특정 섹션 조회"""
    section = await crud_section.get(db, id=section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return section

@router.put("/{section_id}", response_model=Section)
@handle_exceptions()
async def update_section(
    section_id: int,
    section_in: SectionUpdate,
    db: AsyncSession = Depends(get_db)
) -> Section:
    """섹션 정보 수정"""
    section = await crud_section.get(db, id=section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return await crud_section.update(db, db_obj=section, obj_in=section_in)

@router.delete("/{section_id}", response_model=Section)
@handle_exceptions()
async def delete_section(
    section_id: int,
    db: AsyncSession = Depends(get_db)
) -> Section:
    """섹션 삭제"""
    section = await crud_section.remove(db, id=section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return section

@router.put("/document/{document_id}/reorder", response_model=List[Section])
@handle_exceptions()
async def reorder_sections(
    document_id: int,
    section_orders: Dict[int, int],
    db: AsyncSession = Depends(get_db)
) -> List[Section]:
    """문서 내 섹션 순서 변경"""
    return await crud_section.reorder_sections(
        db,
        document_id=document_id,
        section_orders=section_orders
    )
