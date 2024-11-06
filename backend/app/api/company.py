from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from ..models.company import Company
from pydantic import BaseModel

router = APIRouter()

class CompanyCreate(BaseModel):
    name: str
    business_number: str
    company_info: dict

class CompanyResponse(BaseModel):
    id: int
    name: str
    business_number: str
    company_info: dict

    class Config:
        from_attributes = True

@router.post("/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()
