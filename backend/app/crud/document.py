from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document, DocumentType
from app.schemas.document import DocumentCreate, DocumentUpdate
from .base import CRUDBase

class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: DocumentCreate) -> Document:
        """Create new document with error logging"""
        try:
            # Model 인스턴스 생성
            db_obj = Document(
                title=obj_in.title,
                type=obj_in.type,
                content=obj_in.content,
                file_path=obj_in.file_path,
                file_name=obj_in.file_name,
                mime_type=obj_in.mime_type,
                company_id=obj_in.company_id
            )

            print(f"\nCreating document with data: {obj_in.model_dump()}")
            print(f"Created db object: {db_obj.__dict__}")

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            print(f"\nError in document creation: {str(e)}")
            raise

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
