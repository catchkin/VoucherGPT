from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.plan import BusinessPlan
from ..services.gpt_service import GPTService
from ..services.file_service import FileService

router = APIRouter()
gpt_service = GPTService()

@router.post("/generate/{section_type}")
async def generate_plan_content(
        section_type: str,
        company_data: dict,
        files: List[UploadFile] = File(None),
        db: Session = Depends(get_db)
):
    try:
        # 파일 처리
        reference_text = ""
        if files:
            file_service = FileService(db)
            for file in files:
                doc = await file_service.save_file(file)
                if doc.content:
                    reference_text += f"\n{doc.content}"

        # 내용 생성
        content = await gpt_service.generate_plan_content(
            section_type,
            company_data,
            reference_text
        )

        return {"content": content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_plan(
    plan_data: dict,
    db: Session = Depends(get_db)
):
    try:
        plan = BusinessPlan(
            company_data=plan_data["company_data"],
            content=plan_data["content"],
            status="draft"
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))