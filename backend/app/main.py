from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import plan
from .database import engine, Base

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

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
app.include_router(plan.router, prefix="/api/plan", tags=["plan"])
