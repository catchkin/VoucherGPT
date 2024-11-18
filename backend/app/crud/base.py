from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import  BaseModel
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD 객체 초기화

        Args:
            model: SQLAlchemy 모델 클래스
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """ID로 단일 객체 조회"""
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """객체 목록 조회"""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_sorted(
        self,
        db: AsyncSession,
        *,
        sort_by: str,
        order: str = "asc",
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """정렬된 객체 목록 조회"""
        if hasattr(self.model, sort_by):
            order_col = getattr(self.model, sort_by)
            query = select(self.model)

            if order.lower() == "desc":
                query = query.order_by(desc(order_col))
            else:
                query = query.order_by(order_col)
            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        else:
            # 정렬 기준이 없는 경우 기본 정렬
            return await self.get_multi(db, skip=skip, limit=limit)

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """새 객체 생성"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """객체 수정"""
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_id(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """ID로 객체 수정"""
        db_obj = await self.get(db, id)
        if db_obj:
            return await self.update(db, db_obj=db_obj, obj_in=obj_in)
        return None

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        """객체 삭제"""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def remove_multi(self, db: AsyncSession, *, ids: List[int]) -> int:
        """여러 객체 삭제"""
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
