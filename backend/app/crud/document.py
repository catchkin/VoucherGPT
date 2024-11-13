from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import os
from fastapi import status, HTTPException
from app.models.document import Document, DocumentType
from app.models.section import Section, SectionType

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

    async def get(self, db: AsyncSession, *, id: int) -> Optional[Document]:
        """Get a record by ID."""
        try:
            query = select(self.model).where(self.model.id == id)
            result = await db.execute(query)
            document = result.scalar_one_or_none()

            if not document:
                return None

            # 세션 상태 갱신
            await db.refresh(document)
            return document

        except Exception as e:
            await db.rollback()
            return None

    async def remove(self, db: AsyncSession, *, id: int) -> Document:
        """Delete a record."""
        try:
            # 문서 조회 (관련 섹션도 함께 로드)
            query = select(self.model).options(
                selectinload(self.model.sections)
            ).where(self.model.id == id)
            result = await db.execute(query)
            document = result.scalar_one_or_none()

            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )

            try:
                # 파일 삭제
                if document.file_path and os.path.exists(document.file_path):
                    try:
                        os.remove(document.file_path)
                    except OSError:
                        pass  # 파일 삭제 실패는 무시

                # 문서와 관련 섹션 삭제
                await db.delete(document)
                await db.commit()

                # 세션에서 객체 제거
                await db.refresh(document)
                db.expunge_all()  # 세션에서 모든 객체 제거

                return document

            except Exception as e:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete document: {str(e)}"
                )

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

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
