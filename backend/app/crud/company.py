from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from typing import List, Optional

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate

class CompanyCRUD:
    def create(self, db: Session, *, obj_in: CompanyCreate) -> Company:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Company(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.id == id).first()

    def get_by_business_number(self, db: Session, business_number: str) -> Optional[Company]:
        return db.query(Company).filter(Company.business_number == business_number).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit = 100
    ) -> List[Company]:
        return db.query(Company).offset(skip).limit(limit).all()

    def update(
        self,
        db: Session,
        *,
        db_obj: Company,
        obj_in: CompanyUpdate
    ) -> Company:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Company:
        obj = db.query(Company).get(id)
        db.delete(obj)
        db.commit()
        return obj

company = CompanyCRUD()
