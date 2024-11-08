from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.section import Section
from app.schemas.section import SectionCreate, SectionUpdate
from .base import CRUDBase
from .document import document


class CRUDSection(CRUDBase[Section, SectionCreate, SectionUpdate]):
    async def get_by_document(
        self, db: AsyncSession, *, document_id: int, skip: int = 0, limit: int = 100
    ) -> List[Section]:
        """Get sections for a specific document."""
        query = (
            select(self.model)
            .where(self.model.document_id == document_id)
            .order_by(self.model.order)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, section_type: str, skip: int = 0, limit: int = 100
    ) -> List[Section]:
        """Get sections of a specific type."""
        query = (
            select(self.model)
            .where(self.model.type == section_type)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def reorder_sections(
        self, db: AsyncSession, *, document_id: int, section_orders: dict[int, int]
    ) -> List[Section]:
        """Reorder sections in a document."""
        sections = await self.get_by_document(db, document_id=document_id)
        for section in sections:
            if section.id in section_orders:
                section.order = section_orders[section.id]
                db.add(section)
        await db.commit()
        return await self.get_by_document(db, document_id=document_id)

# Create crud_section instance
section = CRUDSection(Section)
