from typing import AsyncGenerator, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import functools

from app.core.database import AsyncSessionLocal
from app.core.config import settings

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션 의존성
    FastAPI 엔드포인트에서 데이터베이스 세션을 주입받을 때 사용
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def handle_exceptions() -> Callable:
    """
    공통 예외 처리를 위한 데코레이터.
    데이터베이스 오류 등을 적절한 HTTP 응답으로 변환.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 데이터베이스 관련 예외
                if "duplicate key" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Resource already exists"
                    )
                # 데이터 무결성 예외
                if "foreign key" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid reference to related resource"
                    )
                # 기타 예외는 서버 에러로 처리
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
        return wrapper
    return decorator

async def validate_file_size(file_size: int) -> None:
    """
    파일 크기 검증 유틸리티.
    설정된 최대 파일 크기를 초과하는 경우 예외 발생.
    """
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE} bytes"
        )

async def validate_mime_type(mime_type: str) -> None:
    """
    파일 MIME 타입 검증 유틸리티.
    허용되지 않는 파일 형식인 경우 예외 발생.
    """
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ]
    if mime_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )

# 공통적으로 사용될 기본 의존성
CommonDeps = {
    "db": Depends(get_db),
}
