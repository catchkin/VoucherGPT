from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.plan import BusinessPlan
from ..models.document import Document
from ..services.gpt_service import GPTService
from pydantic import BaseModel

router = APIRouter()
gpt_service = GPTService()

class PlanCreate(BaseModel):
    company_id: int
    content: dict

class PlanResponse(BaseModel):
    id: int
    company_id: int
    content: dict
    status: str

    class Config:
        from_attributes = True

@router.post("/generate/{section_type}")
async def generate_plan_content(
        section_type: str,
        company_data: dict,
        files: List[UploadFile] = File(None),
        db: Session = Depends(get_db)
):
    try:
        # 회사 정보 조회
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # 파일 처리 및 참조 문서 저장
        reference_texts = []
        if files:
            for file in files:
                content = await file.read()
                if file.content_type == 'text/plain':
                    text_content = content.decode('utf-8')
                    reference_texts.append(text_content)

                # 참조 문서 저장
                doc = Document(
                    name=file.filename,
                    document_type='reference',
                    content=text_content,
                    file_metadata={'content_type': file.content_type}
                )
                db.add(doc)

        db.commit()

        # GPT를 통한 내용 생성
        generated_content = await gpt_service.generate_plan_content(
            section_type=section_type,
            company_data=company.company_info,
            reference_text="\n".join(reference_texts) if reference_texts else None
        )

        return {"content": generated_content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=PlanResponse)
async def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = BusinessPlan(**plan.dict(), status="draft")
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/{company_id}", response_model=List[PlanResponse])
async def get_company_plans(company_id: int, db: Session = Depends(get_db)):
    plans = db.query(BusinessPlan).filter(BusinessPlan.company_id == company_id).all()
    return plans
