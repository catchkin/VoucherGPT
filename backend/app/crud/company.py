from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from .base import CRUDBase

class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    async def get_by_business_number(self, db: AsyncSession, *, business_number: str) -> Optional[Company]:
        """Get a company by business registration number."""
        query = select(self.model).where(self.model.business_number == business_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_relations(self, db: AsyncSession, *, id: int) -> Optional[Company]:
        """Get a company with related documents and sections."""
        query = (
            select(self.model)
            .options(selectinload(self.model.documents))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """Get active companies with pagination."""
        query = (
            select(self.model)
            .where(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

# Create crud_company instance
company = CRUDCompany(Company)