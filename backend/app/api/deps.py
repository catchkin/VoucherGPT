from typing import AsyncGenerator, Callable, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import functools

from app.core.database import AsyncSessionLocal
from app.core.config import settings

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

def handle_exceptions() -> Callable:
    """공통 예외 처리를 위한 데코레이터"""
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
                        detail="리소스가 이미 존재합니다"
                    )
                # 데이터 무결성 예외
                if "foreign key" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="참조하는 리소스가 존재하지 않습니다"
                    )
                # 파일 처리 예와
                if "file" in str(e).lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="파일 처리 중 오류가 발생했습니다"
                    )
                # 기타 예외는 서버 에러로 처리
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="서버 오류가 발생했습니다"
                )
        return wrapper
    return decorator

async def validate_company(
    company_id: int,
    db: AsyncSession = Depends(DatabaseDependency.get_db)
) -> None:
    """회사 ID 유효성 검증 유틸리티"""
    from app.models import Company
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회사를 찾을 수 없습니다"
        )

# 자주 사용되는 의존성 조합
CommonDeps = {
    "db": Depends(DatabaseDependency.get_db),
    "commons": Depends(CommonQueryParams),
}
