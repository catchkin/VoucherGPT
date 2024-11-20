import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.section import SectionType

pytestmark = pytest.mark.asyncio

class TestSectionsAPI:
    async def create_test_document(
        self,
        async_client: AsyncClient,
        valid_company_data: dict,
        valid_document_data: dict
    ):
        """테스트용 회사 및 문서 생성 헬퍼 메서드"""
        # 회사 생성
        company_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        company = company_response.json()

        # 문서 생성
        files = {
            'file': ('test.pdf', b'test content', 'application/pdf')
        }
        data = {
            'title': valid_document_data['title'],
            'type': valid_document_data['type'],
            'company_id': str(company['id'])
        }

        document_response = await async_client.post(
            f"{settings.API_V1_STR}/documents/",
            files=files,
            data=data
        )
        return company_response.json(), document_response.json()

    async def test_create_section(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict,
        valid_section_data: dict
    ):
        """섹션 생성 테스트"""
        # 회사와 문서 생성
        company, document = await self.create_test_document(
            async_client, valid_company_data, valid_document_data
        )

        # 섹션 데이터 준비
        section_data = {
            "title": valid_section_data["title"],
            "type": valid_section_data["type"],
            "content": valid_section_data["content"],
            "order": valid_section_data["order"],
            "document_id": document["id"],
            "company_id": company["id"]
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/sections/",
            json=section_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == section_data["title"]
        assert data["type"] == section_data["type"]
        assert data["document_id"] == document["id"]
        return data

    async def test_get_section(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict,
        valid_section_data: dict
    ):
        """특정 섹션 조회 테스트"""
        section_data = await self.test_create_section(
            async_client,
            db_session,
            valid_company_data,
            valid_document_data,
            valid_section_data
        )

        response = await async_client.get(
            f"{settings.API_V1_STR}/sections/{section_data['id']}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == section_data["id"]
        assert data["title"] == section_data["title"]

    async def test_update_section(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict,
        valid_section_data: dict
    ):
        """섹션 수정 테스트"""
        section_data = await self.test_create_section(
            async_client, db_session, valid_company_data,
            valid_document_data, valid_section_data
        )

        update_data = {
            "title": "Updated Section Title",
            "type": "company_overview",
            "content": "Updated content",
            "order": 2
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/sections/{section_data['id']}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["type"] == update_data["type"]
        assert data["content"] == update_data["content"]

    async def test_delete_section(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict,
        valid_section_data: dict
    ):
        """섹션 삭제 테스트"""
        section_data = await self.test_create_section(
            async_client, db_session, valid_company_data,
            valid_document_data, valid_section_data
        )

        response = await async_client.delete(
            f"{settings.API_V1_STR}/sections/{section_data['id']}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 삭제 확인
        response = await async_client.get(
            f"{settings.API_V1_STR}/sections/{section_data['id']}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_document_sections(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict,
        valid_section_data: dict
    ):
        """문서의 섹션 목록 조회 테스트"""
        section_data = await self.test_create_section(
            async_client, db_session, valid_company_data,
            valid_document_data, valid_section_data
        )

        # 문서의 모든 섹션 조회
        response = await async_client.get(
            f"{settings.API_V1_STR}/sections/document/{section_data['document_id']}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(s["id"] == section_data["id"] for s in data)

        # 섹션 타입으로 필터링
        response = await async_client.get(
            f"{settings.API_V1_STR}/sections/document/{section_data['document_id']}",
            params={"section_type": section_data["type"]}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(s["type"] == section_data["type"] for s in data)

    async def test_get_sections_by_type(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict,
        valid_section_data: dict
    ):
        """섹션 타입별 조회 테스트"""
        section_data = await self.test_create_section(
            async_client, db_session, valid_company_data,
            valid_document_data, valid_section_data
        )

        response = await async_client.get(
            f"{settings.API_V1_STR}/sections/types/",
            params={"section_type": section_data["type"]}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert all(s["type"] == section_data["type"] for s in data)

    async def test_section_not_found(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """존재하지 않는 섹션 조회 테스트"""
        response = await async_client.get(
            f"{settings.API_V1_STR}/sections/99999"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_section_invalid_document(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_section_data: dict
    ):
        """존재하지 않는 문서로 섹션 생성 시도"""
        # 회사만 생성
        company_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        company = company_response.json()

        section_data = {
            **valid_section_data,
            "document_id": 99999,  # 존재하지 않는 문서 ID
            "company_id": company["id"]
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/sections/",
            json=section_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
