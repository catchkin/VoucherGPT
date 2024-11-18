from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    async def get_by_business_number(self, db: AsyncSession, *, business_number: str) -> Optional[Company]:
        """사업자등록번호로 회사 조회"""
        query = select(Company).where(Company.business_number == business_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_companies(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """활성화된 회사 목록 조회"""
        query = select(Company).where(Company.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_sorted_companies(
        self,
        db: AsyncSession,
        *,
        sort_by: str,
        order: str = "asc",
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Company]:
        """정렬된 회사 목록 조회"""
        if hasattr(Company, sort_by):
            order_col = getattr(Company, sort_by)
            query = select(Company)

            if active_only:
                query = query.where(Company.is_active == True)

            if order.lower() == "desc":
                query = query.order_by(desc(order_col))
            else:
                query = query.order_by(order_col)

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        else:
            # 정렬 기준이 없는 경우 기본 정렬
            return await self.get_multi(db, skip=skip, limit=limit)

    async def get_by_industry(
        self, db: AsyncSession, *, industry: str, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """산업 분류별 기업 목록 조회"""
        query = select(Company).where(Company.industry == industry).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update_company_status(
        self, db: AsyncSession, *, company_id: int, is_active: bool
    ) -> Optional[Company]:
        """회사 활성화 상태 변경"""
        company = await self.get(db, id=company_id)
        if company:
            company.is_active = is_active
            db.add(company)
            await db.commit()
            await db.refresh(company)
        return company

    async def search_companies(
        self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """회사 검색"""
        search = f"%{query}%"
        query = select(Company).where(
            (Company.name.ilike(search)) |
            (Company.industry.ilike(search)) |
            (Company.description.ilike(search))
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

company = CRUDCompany(Company)
