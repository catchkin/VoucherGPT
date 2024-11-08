from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.utils import status_code_ranges
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, handle_exceptions
from app.crud import crud_company
from app.schemas import CompanyCreate, CompanyUpdate, Company, CompanyWithRelations

router = APIRouter()

@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
@handle_exceptions()
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db)
) -> Company:
    """새로운 회사 생성"""
    return await crud_company.create(db, obj_in=company_in)

@router.get("/", response_model=List[Company])
@handle_exceptions()
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Company]:
    """회사 목록 조회"""
    return await crud_company.get_multi(db, skip=skip, limit=limit)

@router.get("/{company_id}", response_model=Company)
@handle_exceptions()
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
) -> Company:
    """특정 회사 조회"""
    company = await crud_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company

@router.get("/{company_id}/full", response_model=CompanyWithRelations)
@handle_exceptions()
async def get_company_with_relations(
    company_id: int,
    db: AsyncSession = Depends(get_db)
) -> CompanyWithRelations:
    """회사 정보를 관련 문서들과 함께 조회"""
    company = await crud_company.get_with_relations(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company

@router.put("/{company_id}", response_model=Company)
@handle_exceptions()
async def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
) -> Company:
    """회사 정보 수정"""
    company = await crud_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return await crud_company.update(db, db_obj=company, obj_in=company_in)

@router.delete("/{company_id}", response_model=Company)
@handle_exceptions()
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
) -> Company:
    """회사 삭제"""
    company = await crud_company.remove(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company
