from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from .base import CRUDBase

class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    async def get_by_business_number(self, db: AsyncSession, *, business_number: str) -> Optional[Company]:
        """사업자등록번호로 기업 조회"""
        query = select(self.model).where(self.model.business_number == business_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_companies(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """활성화된 기업 목록 조회"""
        query = select(self.model)\
            .where(self.model.is_active == True)\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_industry(
        self, db: AsyncSession, *, industry: str, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """산업 분류별 기업 목록 조회"""
        query = select(self.model)\
            .where(self.model.industry == industry)\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def deactivate(self, db: AsyncSession, *, id: int) -> Optional[Company]:
        """기업 비활성화"""
        obj = await self.get(db=db, id=id)
        if obj:
            obj.is_active = False
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
        return obj

company = CRUDCompany(Company)