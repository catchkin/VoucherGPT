from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import company, plan

app = FastAPI(title="VoucherGPT")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(company.router, prefix="/api/companies", tags=["companies"])
app.include_router(plan.router, prefix="/api/plans", tags=["plans"])
