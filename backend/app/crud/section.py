from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Section, SectionType
from app.schemas.section import SectionCreate, SectionUpdate


class CRUDSection(CRUDBase[Section, SectionCreate, SectionUpdate]):
    async def create_with_order(
        self,
        db: AsyncSession,
        *,
        obj_in: SectionCreate
    ) -> Section:
        """순서 자동 할당하여 섹션 생성"""
        # 현재 문서의 최대 순서 값 조회
        query = select(func.max(Section.order)).where(
            Section.document_id == obj_in.document_id
        )
        result = await db.execute(query)
        max_order = result.scalar() or 0

        # 데이터 준비
        db_data = obj_in.model_dump()
        db_data["order"] == max_order + 1

        # 섹션 생성
        db_obj = Section(**db_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_document(
        self,
        db: AsyncSession,
        *,
        document_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Section]:
        """문서별 섹션 목록 조회"""
        query = (
            select(Section)
            .where(Section.document_id == document_id)
            .order_by(Section.order)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self,
        db: AsyncSession,
        *,
        section_type: SectionType,
        document_id: Optional[int] = None,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Section]:
        """섹션 유형별 조회"""
        conditions = [Section.type == section_type]
        if document_id:
            conditions.append(Section.document_id == document_id)
        if company_id:
            conditions.append(Section.company_id == company_id)

        query = (
            select(Section)
            .where(and_(*conditions))
            .order_by(Section.order)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def update_order(
        self,
        db: AsyncSession,
        *,
        section_id: int,
        new_order: int
    ) -> Optional[Section]:
        """섹션 순서 변경"""
        # 현재 섹션 조회
        section = await self.get(db, id=section_id)
        if not section:
            return None

        old_order = section.order

        # 같은 문서 내의 다른 섹션들 순서 조정
        if new_order > old_order:
            # 위로 이동: 중간 섹션들의 순서를 하나씩 감소
            query = (
                select(Section)
                .where(
                    and_(
                        Section.document_id == section.document_id,
                        Section.order <= new_order,
                        Section.order > old_order
                    )
                )
            )
            result = await db.execute(query)
            affected_sections = result.scalars().all()
            for affected in affected_sections:
                affected.order -= 1
        else:
            # 아래로 이동: 중간 섹션들의 순서를 하나씩 증가
            query = (
                select(Section)
                .where(
                    and_(
                        Section.document_id == section.document_id,
                        Section.order >= new_order,
                        Section.order < old_order
                    )
                )
            )
            result = await db.execute(query)
            affected_sections = result.scalars().all()
            for affected in affected_sections:
                affected.order += 1

        # 현재 섹션 순서 업데이트
        section.order = new_order
        await db.commit()
        await db.refresh(section)
        return section

    async def search_sections(
        self,
        db: AsyncSession,
        *,
        query: str,
        document_id: Optional[int] = None,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Section]:
        """색션 검색"""
        search_term = f"%{query}%"
        conditions = [
            Section.title.ilike(search_term) |
            Section.content.ilike(search_term)
        ]
        if document_id:
            conditions.append(Section.document_id == document_id)
        if company_id:
            conditions.append(Section.company_id == company_id)

        query = (
            select(Section)
            .where(and_(*conditions))
            .order_by(Section.order)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

# CRUD 객체 인스턴스 생성
section = CRUDSection(Section)
