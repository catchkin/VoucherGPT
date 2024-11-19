import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Company

pytestmark = pytest.mark.asyncio

class TestCompaniesAPI:
    @pytest.mark.asyncio
    async def test_create_company(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict
    ):
        """회사 생성 API 테스트"""
        response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == valid_company_data["name"]
        assert data["business_number"] == valid_company_data["business_number"]

    async def test_create_company_duplicate_business_number(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict
    ):
        """중복된 사업자번호로 회사 생성 시도"""
        await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )

        # 같은 데이터로 두 번째 생성 시도
        response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_read_companies(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict
    ):
        """회사 목록 조회 API 테스트"""
        # 테스트용 회사 생성
        await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )

        response = await async_client.get(
            f"{settings.API_V1_STR}/companies/"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(c["business_number"] == valid_company_data["business_number"] for c in data)

    async def test_read_company(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict
    ):
        """특정 회사 조회 API 테스트"""
        # 회사 생성
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        created_company = create_response.json()

        response = await async_client.get(
            f"{settings.API_V1_STR}/companies/{created_company['id']}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == valid_company_data["name"]
        assert data["business_number"] == valid_company_data["business_number"]

    async def test_update_company(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict
    ):
        """회사 정보 업데이트 API 테스트"""
        # 회사 생성
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        created_company = create_response.json()

        # 업데이트 데이터
        update_data = {
            "name": "Updated Company Name",
            "employee_count": 100,
            "description": "Updated description"
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/companies/{created_company['id']}",
            json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["employee_count"] == update_data["employee_count"]
        assert data["business_number"] == valid_company_data["business_number"]

    async def test_delete_company(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict
    ):
        """회사 삭제 API 테스트"""
        # 회사 생성
        create_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        created_company = create_response.json()

        # 삭제
        response = await async_client.delete(
            f"{settings.API_V1_STR}/companies/{created_company['id']}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 삭제 확인
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/companies/{created_company['id']}"
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_company_not_found(
            self,
            async_client: AsyncClient,
            db_session: AsyncSession
    ):
        """존재하지 않는 회사 조회 시 404 반환 테스트"""
        response = await async_client.get(
            f"{settings.API_V1_STR}/companies/99999"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
