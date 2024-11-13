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

from app.models.document import Document, DocumentType
from app.models.company import Company
from app.models.section import Section, SectionType
from app.schemas.company import CompanyCreate

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
            print("\nCreating new test database session")
            yield session
        finally:
            print("\nClosing test database session")
            await session.close()


@pytest.fixture
async def client(session: AsyncSession):
    """Create test client with database session override."""
    async def override_get_db():
        try:
            yield session
        finally:
            await session.close()

    print("\nSetting up test client with database override")
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def test_upload_dir():
    """Create and clean up test upload directory."""
    test_dir = "test_uploads"
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir
    # Clean up
    for file in os.listdir(test_dir):
        os.remove(os.path.join(test_dir, file))
    os.rmdir(test_dir)

# Document Test Fixtures
@pytest.fixture
async def create_company(session: AsyncSession) -> Company:
    """Create test company"""
    company_data = {
        "name": "Test Company",
        "business_number": "123-45-67890",
        "industry": "Technology",
        "establishment_date": "2020-01-01",
        "employee_count": 50,
        "annual_revenue": 1000000,
        "description": "Test company description"
    }
    company = Company(**company_data)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company

@pytest.fixture
async def create_document(session: AsyncSession, create_company: Company) -> Document:
    """Create test document"""
    document = Document(
        title="Test Document",
        type=DocumentType.BUSINESS_PLAN,
        content="Test content",
        company_id=create_company.id  # company_id 추가
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@pytest.fixture
async def create_multiple_documents(session: AsyncSession, create_company: Company) -> list[Document]:
    """Create multiple test documents."""
    documents = []
    for i in range(3):
        document = Document(
            title=f"Test Document {i}",
            type=DocumentType.BUSINESS_PLAN,
            content=f"Test content {i}",
            company_id=create_company.id
        )
        session.add(document)
        documents.append(document)

    await session.commit()
    for doc in documents:
        await session.refresh(doc)
    return documents


@pytest.fixture
async def create_section(session: AsyncSession, create_document: Document) -> Section:
    """Create test section."""
    section = Section(
        type=SectionType.EXECUTIVE_SUMMARY,
        title="Test Section",
        content="Test section content",
        order=0,
        document_id=create_document.id,
        company_id=create_document.company_id  # company_id 추가
    )
    session.add(section)
    await session.commit()
    await session.refresh(section)
    return section

@pytest.fixture
async def create_document_with_sections(
        session: AsyncSession,
        create_company: Company
) -> Document:
    """Create test document with multiple sections."""
    # Create document
    document = Document(
        title="Test Document with Sections",
        type=DocumentType.BUSINESS_PLAN,
        content="Test content",
        company_id=create_company.id
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)

    # Create sections
    sections = [
        Section(
            type=SectionType.EXECUTIVE_SUMMARY,
            title="Executive Summary",
            content="Test executive summary",
            order=0,
            document_id=document.id,
            company_id=create_company.id
        ),
        Section(
            type=SectionType.COMPANY_OVERVIEW,
            title="Company Overview",
            content="Test company overview",
            order=1,
            document_id=document.id,
            company_id=create_company.id
        ),
        Section(
            type=SectionType.BUSINESS_MODEL,
            title="Business Model",
            content="Test business model",
            order=2,
            document_id=document.id,
            company_id=create_company.id
        )
    ]

    for section in sections:
        session.add(section)

    await session.commit()
    await session.refresh(document)
    return document


async def clear_test_data(session: AsyncSession):
    """Clear all test data from database."""
    await session.execute(Section.__table__.delete())
    await session.execute(Document.__table__.delete())
    await session.execute(Company.__table__.delete())
    await session.commit()

@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """각 테스트 케이스 실행 전후로 테이블 초기화"""
    await clear_test_data(session)
    yield
    await clear_test_data(session)