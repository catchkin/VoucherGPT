from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps

from apitest1 import response

router = APIRouter()

@router.post("/", response_mode=schemas.Company)
def create_company(
    *,
    db: Session = Depends(deps.get_db),
    company_in: schemas.CompanyCreate,
) -> Any:
    """
    새로운 기업 생성
    """
    company = crud.company.get_by_business_number(db, business_number=company_in.business_number)
    if company:
        raise HTTPException(
            status_code=400,
            detail="The company with this business number already exists in the system.",
        )
    company = crud.company.create(db, obj_in=company_in)
    return company

@router.get("/", response_model=List[schemas.Company])
def read_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    기업 목록 조회
    """
    companies = crud.company.get_multi(db, skip=skip, limit=limit)
    return companies

@router.get("/{company_id}", response_model=schemas.Company)
def read_company(
    company_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    기업 정보 조회
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=schemas.Company)
def update_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    company_in: schemas.CompanyUpdate,
) -> Any:
    """
    기업 정보 수정
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not foudn")
    company = crud.company.update(db, db_obj=company, obj_in=company_in)
    return company

@router.delete("/{company_id}", response_model=schemas.Company)
def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
) -> Any:
    """
    기업 삭제
    """
    company = crud.company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Companies not found")
    company = crud.company.remove(db, id=company_id)
    return company
