import asyncio
from typing import AsyncGenerator, Generator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.core.database import Base, get_async_db
from app.main import app

# 테스트용 데이터베이스 URL 설정
TEST_SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://vouchergpt_user:blogcodi0318@localhost:5432/vouchergpt_test"

# 테스트용 엔진 생성
test_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    echo=False,  # 테스트 시 SQL 로그 비활성화
)

# 테스트용 세션 팩토리
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 데이터베이스 세션"""
    async with test_engine.begin() as conn:
        # 각 테스트 전에 모든 테이블을 새로 생성
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        # 세션 롤백
        await session.rollback()
        # 세션 종료
        await session.close()

@pytest.fixture(scope="function")
def client() -> Generator:
    """FastAPI 테스트 클라이언트"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def override_get_db(db_session: AsyncSession):
    """DB 의존성 오버라이드"""
    async def get_test_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_async_db] = get_test_db  # database.py의 get_async_db 사용
    yield
    app.dependency_overrides.clear()


# 테스트에 필요한 기본 데이터를 제공하는 fixture들만 정의
@pytest.fixture(scope="module")
def valid_company_data() -> dict:
    return {
        "name": "테스트 기업",
        "business_number": "1234567890",
        "industry": "IT",
        "establishment_date": "2020-01-01",
        "employee_count": 50,
        "annual_revenue": 1000000000,
        "description": "테스트 기업 설명",
        "target_markets": ["국내", "해외"],
        "export_countries": ["미국", "일본"],
        "export_history": {"2023": {"amount": 500000}}
    }

@pytest.fixture(scope="module")
def valid_document_data() -> dict:
    return {
        "company_id": 1,
        "title": "사업계획서",
        "type": "business_plan",
        "content": "테스트 내용",
        "file_name": "test.pdf",
        "mime_type": "application/pdf",
        "doc_metadata": {"version": "1.0"}
    }

@pytest.fixture(scope="module")
def valid_section_data() -> dict:
    return {
        "document_id": 1,
        "company_id": 1,
        "type": "executive_summary",
        "title": "요약",
        "content": "테스트 내용",
        "order": 1,
        "meta_data": {"status": "draft"}
    }