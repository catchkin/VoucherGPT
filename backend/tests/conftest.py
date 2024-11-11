# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

from app.main import app
from app.core.config import settings
from app.core.database import Base
from app.api.deps import get_db

# 환경변수 로드
load_dotenv()

# 테스트 데이터베이스 URL 설정
DB_USER = os.getenv("DB_USER", "vouchergpt_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "blogcodi0318")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = "vouchergpt_test"

TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 테스트용 엔진 설정
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

# 테스트용 세션 팩토리
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine_fixture():
    """Create test engine fixture."""
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def test_db():
    """Create test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
async def client(session: AsyncSession):
    """Create test client with database session override."""
    async def override_get_db():
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac
    app.dependency_overrides.clear()