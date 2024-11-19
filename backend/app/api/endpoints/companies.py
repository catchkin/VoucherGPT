from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps
from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate, CompanyInDB
from app.crud.company import company

router = APIRouter()

@router.post("/", response_model=CompanyInDB, status_code=status.HTTP_201_CREATED)
@deps.handle_exceptions()
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """새로운 회사 등록"""
    # 사업자번호 중복 체크
    existing_company = await company.get_by_business_number(
        db=db,
        business_number=company_in.business_number
    )
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business number already registered"
        )

    return await company.create(db, obj_in=company_in)

@router.get("/", response_model=List[CompanyInDB])
@deps.handle_exceptions()
async def get_companies(
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db),
    commons: deps.CommonQueryParams = Depends()
):
    """회사 목록 조회"""
    if commons.sort_by:
        return await company.get_sorted(db, sort_by=commons.sort_by, order=commons.order,
                                        skip=commons.skip, limit=commons.limit)
    return await company.get_multi(db, skip=commons.skip, limit=commons.limit)

@router.get("/{company_id}", response_model=CompanyInDB)
@deps.handle_exceptions()
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """특정 회사 정보 조회"""
    db_company = await company.get(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/{company_id}", response_model=CompanyInDB)
@deps.handle_exceptions()
async def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """회사 정보 수정"""
    db_company = await company.get(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return await company.update(db, db_obj=db_company, obj_in=company_in)

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
@deps.handle_exceptions()
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(deps.DatabaseDependency.get_db)
):
    """회사 삭제"""
    db_company = await company.get(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    await company.remove(db, id=company_id)
