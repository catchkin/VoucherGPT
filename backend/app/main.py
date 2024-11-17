from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import os

from app.core.config import settings
#from app.api.endpoints import companies, documents, sections

# 업로드 디렉토리 생성
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="VoucherGPT API documentation",
    # docs_url과 redoc_url에서 prefix 제거
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# 정적 파일 서빙 설정 (업로드된 파일용)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API 라우터 등록
#app.include_router(
#    companies.router,
#    prefix=f"{settings.API_V1_STR}/companies",
#    tags=["companies"]
#)
#app.include_router(
#    documents.router,
#    prefix=f"{settings.API_V1_STR}/documents",
#    tags=["documents"]
#)
#app.include_router(
#    sections.router,
#    prefix=f"{settings.API_V1_STR}/sections",
#    tags=["sections"]
#)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """요청 검증 에러 핸들링"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": exc.errors()
        }
    )

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Welcome to VoucherGPT API",
        "version": "0.1.0",
        "docs_urls": {
            "Swagger UI": "/docs",
            "ReDoc": "/redoc",
            "OpenAPI JSON": "/api/v1/openapi.json"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
