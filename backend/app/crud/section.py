from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.section import Section, SectionType
from app.schemas.section import SectionCreate, SectionUpdate
from .base import CRUDBase

class CRUDSection(CRUDBase[Section, SectionCreate, SectionUpdate]):
    async def get_by_document(
        self, db: AsyncSession, *, document_id: int
    ) -> List[Section]:
        """문서별 섹션 목록 조회"""
        query = select(self.model)\
            .where(self.model.document_id == document_id)\
            .order_by(self.model.order)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, section_type: SectionType
    ) -> List[Section]:
        """섹션 유형별 조회"""
        query = select(self.model)\
            .where(self.model.type == section_type)\
            .order_by(self.model.order)
        result = await db.execute(query)
        return result.scalars().all()

    async def reorder_sections(
        self, db: AsyncSession, *, document_id: int, section_orders: dict[int, int]
    ) -> List[Section]:
        """섹션 순서 재정렬"""
        sections = await self.get_by_document(db=db, document_id=document_id)
        for section in sections:
            if section.id in section_orders:
                section.order = section_orders[section.id]
                db.add(section)

        await db.commit()
        return sections

    async def get_by_company(
        self, db: AsyncSession, *, company_id: int
    ) -> List[Section]:
        """기업별 모든 섹션 조회"""
        query = select(self.model) \
            .where(self.model.company_id == company_id) \
            .order_by(self.model.document_id, self.model.order)
        result = await db.execute(query)
        return result.scalars().all()

section = CRUDSection(Section)
