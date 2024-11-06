from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import company_router

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
app.include_router(company_router, prefix="/api/companies", tags=["companies"])
