from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import os
import shutil
from datetime import datetime

from app.crud.base import CRUDBase
from app.models import Document, DocumentType
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.config import settings


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    async def get_by_company(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """회사별 문서 목록 조회"""
        query = (
            select(Document)
            .where(Document.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self,
        db: AsyncSession,
        *,
        doc_type: DocumentType,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """문서 유형별 조회"""
        conditions = [Document.type == doc_type]
        if company_id:
            conditions.append(Document.company_id == company_id)

        query = (
            select(Document)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create_with_file(
        self,
        db: AsyncSession,
        *,
        obj_in: DocumentCreate,
        file: UploadFile
    ) -> Document:
        """파일과 함께 문서 생성"""
        try:
            # 회사별 업로드 디렉토리 생성
            company_upload_dir = os.path.join(settings.UPLOAD_DIR, str(obj_in.company_id))
            os.makedirs(company_upload_dir, exist_ok=True)

            # 파일명 생성 (타임스탬프 추가하여 중복 방지)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{file.filename}"
            file_path = os.path.join(company_upload_dir, file_name)

            # 파일 저장
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 문서 데이터 준비
            db_data = obj_in.model_dump()
            db_data.update({
                "file_path": file_path,
                "file_name": file.filename,
                "mime_type": file.content_type
            })

            # DB에 문서 정보 저장
            db_obj = Document(**db_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)

            return db_obj

        except Exception as e:
            #  파일이 저장된 경우 삭제
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            return e

    async def update_with_file(
        self,
        db: AsyncSession,
        *,
        db_obj: Document,
        obj_in: Union[DocumentUpdate, Dict[str, Any]],
        file: Optional[UploadFile] = None
    ) -> Document:
        """파일과 함께 문서 정보 수정"""
        try:
            # 기존 데이터로 update_data 초기화
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            if file:
                # 이전 파일 경로 저장
                old_file_path = db_obj.file_path

                # 새 파일 저장
                company_upload_dir = os.path.join(settings.UPLOAD_DIR, str(db_obj.company_id))
                os.makedirs(company_upload_dir, exist_ok=True)

                # 파일명 생성 (타임스탬프 추가)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{timestamp}_{file.filename}"
                new_file_path = os.path.join(company_upload_dir, file_name)

                # 새 파일 저장
                with open(new_file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                # 파일 관련 정보 업데이트
                update_data.update({
                    "file_path": new_file_path,
                    "file_name": file.filename,
                    "mime_type": file.content_type
                })

                # DB 업데이트 성공 후 이전 파일 삭제
                db_obj = await super().update(db, db_obj=db_obj, obj_in=update_data)
                if old_file_path and os.path.exists(old_file_path):
                    os.remove(old_file_path)
            else:
                # 파일 없이 문서 정보만 업데이트
                db_obj = await super().update(db, db_obj=db_obj, obj_in=update_data)

            return db_obj

        except Exception as e:
            # 새 파일이 저장된 경우 삭제
            if file and 'new_file_path' in locals() and os.path.exists(new_file_path):
                os.remove(new_file_path)
            raise e

    async def remove_with_file(
        self,
        db: AsyncSession,
        *,
        id:int
    ) -> Optional[Document]:
        """문서와 파일 함께 삭제"""
        document = await self.get(db, id=id)
        if document:
            # 파일 삭제
            if document.file_path and os.path.exists(document.file_path):
                try:
                    os.remove(document.file_path)
                except Exception as e:
                    # 파일 삭제 실패 로깅
                    print(f"Error deleting file {document.file_path}: {str(e)}")

            # DB에서 문서 정보 삭제
            await db.delete(document)
            await db.commit()
        return document

    async def search_documents(
        self,
        db: AsyncSession,
        *,
        query: str,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """문서 검색"""
        search_term = f"%{query}%"
        conditions = [
            Document.title.ilike(f"%{query}%") |
            Document.content.ilike(f"%{query}%")
        ]
        if company_id:
            conditions.append(Document.company_id == company_id)

        query = (
            select(Document)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

# CRUD 객체 인스턴스 생성
document = CRUDDocument(Document)
