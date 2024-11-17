from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentType
from app.schemas.document import DocumentCreate, DocumentUpdate
from .base import CRUDBase

class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    async def get_by_company(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """기업별 문서 목록 조회"""
        query = select(self.model)\
            .where(self.model.company_id == company_id)\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, *, doc_type: DocumentType, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """문서 유형별 조회"""
        query = select(self.model)\
            .where(self.model.type == doc_type)\
            .offset(skip)\
            .limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def et_company_documents_by_type(
        self, db: AsyncSession, *, company_id: int, doc_type: DocumentType
    ) -> List[Document]:
        """기업별 특정 유형의 문서 조회"""
        query = select(self.model)\
            .where(self.model.company_id == company_id)\
            .where(self.model.type == doc_type)
        result = await db.execute(query)
        return result.scalars().all()

document = CRUDDocument(Document)
