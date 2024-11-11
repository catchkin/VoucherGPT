from pickle import FALSE

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient, session: AsyncSession):
    """회사 생성 테스트"""
    company_data = {
        "name": "Test Company",
        "business_number": "123-45-67890",
        "industry": "Technology",
        "establishment_date": "2024-01-01",
        "employee_count": 50,
        "annual_revenue": 1000000,
        "description": "Test company description",
        "is_active": True
    }

    response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Content-Type": "application/json"}
    )

    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response content: {response.text}")

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == company_data["name"]
    assert data["business_number"] == company_data["business_number"]

@pytest.mark.asyncio
async def test_get_company(client: AsyncClient, session: AsyncSession):
    """회사 조회 테스트"""
    # 먼저 회사 생성
    company_data = {
        "name": "Company to Get",
        "business_number": "123-45-67891",
        "industry": "IT",
        "is_active": True
    }

    create_response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Content-Type": "application/json"}
    )
    assert create_response.status_code == 201
    created_company = create_response.json()

    # 생성된 회사 조회
    response = await client.get(f"/api/v1/companies/{created_company['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == company_data["name"]
    assert data["business_number"] == company_data["business_number"]


@pytest.mark.asyncio
async def test_update_company(client: AsyncClient, session: AsyncSession):
    """회사 정보 수정 테스트"""
    # 회사 생성
    initial_data = {
        "name": "Original Company",
        "business_number": "123-45-67894",
        "industry": "Manufacturing",
        "is_active": True
    }

    create_response = await client.post(
        "/api/v1/companies/",
        json=initial_data,
        headers={"Content-Type": "application/json"}
    )
    assert create_response.status_code == 201
    created_company = create_response.json()

    # 회사 정보 수정
    update_data = {
        "name": "Updated Company",
        "industry": "Technology",
        "description": "Updated description"
    }

    response = await client.put(
        f"/api/v1/companies/{created_company['id']}",
        json=update_data
    )
    assert response.status_code == 200

    updated_data = response.json()
    assert updated_data["name"] == update_data["name"]
    assert updated_data["industry"] == update_data["industry"]
    assert updated_data["description"] == update_data["description"]
    assert updated_data["business_number"] == initial_data["business_number"]  # 변경되지 않은 필드 확인

@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient, session: AsyncSession):
    """회사 목록 조회 테스트"""
    # 여러 회사 생성
    companies = [
        {
            "name": "Company A",
            "business_number": "123-45-67892",
            "industry": "Finance",
            "is_active": True
        },
        {
            "name": "Company B",
            "business_number": "123-45-67893",
            "industry": "Healthcare",
            "is_active": True
        }
    ]

    # 회사들 생성
    for company in companies:
        response = await client.post(
            "/api/v1/companies/",
            json=company,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201

    # 회사 목록 조회
    response = await client.get("/api/v1/companies/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # 페이지네이션 테스트
    response = await client.get("/api/v1/companies/?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

@pytest.mark.asyncio
async def test_delete_company(client: AsyncClient, session: AsyncSession):
    """회사 삭제 테스트"""
    # 1. 회사 생성
    company_data = {
        "name": "Company to Delete",
        "business_number": "123-45-67895",
        "industry": "Retail",
        "is_active": True
    }

    # 회사 생성
    create_response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Content-Type": "application/json"}
    )
    assert create_response.status_code == 201
    created_company = create_response.json()
    company_id = created_company["id"]

    # DB에서 회사 존재 확인
    query = text("SELECT COUNT(*) FROM companies WHERE id = :id")
    result = await session.execute(query, {"id": company_id})
    assert result.scalar() == 1, "Company was not created in database"

    # 회사 삭제
    delete_response = await client.delete(f"/api/v1/companies/{company_id}")
    assert delete_response.status_code == 200

    # DB에서 회사가 삭제되었는지 직접 확인
    await session.commit()  # 트랜잭션 커밋 보장
    result = await session.execute(query, {"id": company_id})
    assert result.scalar() == 0, "Company was not deleted from database"

    # API를 통한 조회는 404나 500 둘 다 허용
    get_response = await client.get(f"/api/v1/companies/{company_id}")
    assert get_response.status_code in [404, 500], \
        f"Expected 404 or 500, got {get_response.status_code}. Response: {get_response.text}"


@pytest.mark.asyncio
async def test_update_company(client: AsyncClient, session: AsyncSession):
    """회사 정보 수정 테스트"""
    # 1. 회사 생성
    company_data = {
        "name": "Original Company",
        "business_number": "123-45-67896",
        "industry": "IT",
        "is_active": True
    }

    create_response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Content-Type": "application/json"}
    )

    assert create_response.status_code == 201
    created_company = create_response.json()

    # 2. 회사 정보 수정
    update_data = {
        "name": "Updated Company",
        "industry": "Technology"
    }

    update_response = await client.put(
        f"/api/v1/companies/{created_company['id']}",
        json=update_data
    )

    assert update_response.status_code == 200
    updated_company = update_response.json()
    assert updated_company["name"] == update_data["name"]
    assert updated_company["industry"] == update_data["industry"]


@pytest.mark.asyncio
async def test_get_nonexistent_company(client: AsyncClient):
    """존재하지 않는 회사 조회 테스트"""
    response = await client.get("/api/v1/companies/99999")
    assert response.status_code in [404, 500]


async def clear_all_tables(session: AsyncSession):
    """모든 테이블의 데이터를 삭제하고 ID 시퀀스를 리셋"""
    try:
        # 외래키 제약조건 임시 비활성화
        await session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        # 모든 관련 테이블 비우기
        await session.execute(text("TRUNCATE TABLE companies, documents, sections RESTART IDENTITY CASCADE"))
        await session.commit()
        logger.info("Successfully cleared all tables")
    except Exception as e:
        logger.error(f"Error clearing tables: {e}")
        await session.rollback()
        raise


@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """각 테스트 전후로 데이터베이스 초기화"""
    await clear_all_tables(session)
    yield
    await clear_all_tables(session)
