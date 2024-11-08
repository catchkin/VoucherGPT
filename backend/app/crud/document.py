from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from .base import CRUDBase

class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    async def get_by_company(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get documents for a specific company."""
        query = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_sections(self, db: AsyncSession, *, id: int) -> Optional[Document]:
        """Get a document with its sections."""
        query = (
            select(self.model)
            .options(selectinload(self.model.sections))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_type(
        self, db: AsyncSession, *, doc_type: str, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get documents of a specific type."""
        query = (
            select(self.model)
            .where(self.model.type == doc_type)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

# Create crud_document instance
document = CRUDDocument(Document)
