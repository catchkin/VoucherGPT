from typing import AsyncGenerator, Callable, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import functools

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models import Company

class DatabaseDependency:
    """데이터베이스 세션 관리를 위한 의존성 클래스"""

    @staticmethod
    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        """데이터베이스 세션 의존성"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

class CommonQueryParams:
    """공통 쿼리 파라미터"""
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc"
    ):
        self.skip = skip
        self.limit = min(limit, 100)
        self.sort_by = sort_by
        self.order = order.lower() if order else "asc"

        if self.order not in ["asc", "desc"]:
            self.order = "asc"

async def validate_file_type(content_type: str) -> None:
    """파일 타입 검증

    Args:
        content_type: MIME 타입 문자열

    Raises:
        HTTPException: 허용되지 않는 파일 타입인 경우
    """
    allowed_types = [
        'application/pdf',
        'application/msword',  # .doc
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/vnd.ms-excel',  # .xls
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'application/vnd.ms-powerpoint',  # .ppt
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
        'text/plain',  # .txt
        'text/csv',  # .csv
        'application/json'  # .json
    ]

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
        )

async def validate_file_size(file_size: int) -> None:
    """파일 크기 검증

    Args:
        file_size: 파일 크기 (bytes)

    Raises:
        HTTPException: 파일 크기가 제한을 초과하는 경우
    """
    max_size = settings.MAX_UPLOAD_SIZE
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the limit of {max_size / 1024 / 1024:.1f}MB"
        )

async def validate_company(
    company_id: int,
    db: AsyncSession = Depends(DatabaseDependency.get_db)
) -> None:
    """회사 ID 유효성 검증 유틸리티"""
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

def handle_exceptions() -> Callable:
    """공통 예외 처리를 위한 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                # 데이터베이스 관련 예외
                if "duplicate key" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="리소스가 이미 존재합니다"
                    )
                # 데이터 무결성 예외
                if "foreign key" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="참조하는 리소스가 존재하지 않습니다"
                    )
                # 파일 처리 예외
                if "file" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="파일 처리 중 오류가 발생했습니다"
                    )
                # 기타 예외는 서버 에러로 처리
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e) if settings.DEBUG else "서버 오류가 발생했습니다"
                )
        return wrapper
    return decorator


# 자주 사용되는 의존성 조합
CommonDeps = {
    "db": Depends(DatabaseDependency.get_db),
    "commons": Depends(CommonQueryParams),
}
