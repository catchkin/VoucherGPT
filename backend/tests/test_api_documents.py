import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import DocumentType

pytestmark = pytest.mark.asyncio

class TestDocumentsAPI:
    async def test_create_document(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict
    ):
        """문서 생성 API 테스트"""
        # 회사 생성
        company_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        company = company_response.json()

        # Form 데이터와 파일 준비
        files = {
            'file': ('test.pdf', b'test content', 'application/pdf')
        }
        data = {
            'title': valid_document_data['title'],
            'type': valid_document_data['type'],
            'company_id': str(company['id'])
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/documents/",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['title'] == valid_document_data['title']
        assert data['type'] == valid_document_data['type']
        assert data['company_id'] == company['id']
        return data

    async def test_update_document(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict
    ):
        """문서 수정 테스트"""
        # 먼저 문서 생성
        document_data = await self.test_create_document(
            async_client, db_session, valid_company_data, valid_document_data
        )

        # 수정할 데이터 준비
        files = {
            'file': ('updated.pdf', b'updated content', 'application/pdf')
        }
        update_data = {
            'title': 'Updated Document Title',
            'type': DocumentType.COMPANY_PROFILE.value
        }

        response = await async_client.put(
            f"{settings.API_V1_STR}/documents/{document_data['id']}",
            files=files,
            data=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['title'] == update_data['title']
        assert data['type'] == update_data['type']
        # 파일이 업데이트된 경우에만 file_path 확인
        if 'file_path' in data and 'file_path' in document_data:
            assert data['file_path'] != document_data['file_path']

        # 파일 없이 정보만 수정
        update_data = {
            'title': 'Only Title Updated'
        }
        response = await async_client.put(
            f"{settings.API_V1_STR}/documents/{document_data['id']}",
            data=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['title'] == update_data['title']

    async def test_get_company_documents(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict
    ):
        """회사의 문서 목록 조회 테스트"""
        document_data = await self.test_create_document(
            async_client, db_session, valid_company_data, valid_document_data
        )

        # 전체 문서 조회
        response = await async_client.get(
            f"{settings.API_V1_STR}/documents/company/{document_data['company_id']}"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(d['id'] == document_data['id'] for d in data)

        # 문서 타입으로 필터링
        response = await async_client.get(
            f"{settings.API_V1_STR}/documents/company/{document_data['company_id']}",
            params={'document_type': document_data['type']}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(d['type'] == document_data['type'] for d in data)

    async def test_invalid_file_type(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_company_data: dict,
        valid_document_data: dict
    ):
        """잘못된 파일 형식 테스트"""
        # 회사 생성
        company_response = await async_client.post(
            f"{settings.API_V1_STR}/companies/",
            json=valid_company_data
        )
        company = company_response.json()

        # 잘못된 파일 형식으로 시도
        files = {
            'file': ('test.exe', b'invalid content', 'application/x-msdownload')
        }
        data = {
            'title': valid_document_data['title'],
            'type': valid_document_data['type'],
            'company_id': str(company['id'])
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/documents/",
            files=files,
            data=data
        )
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    async def test_document_not_found(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """존재하지 않는 문서 조회 테스트"""
        response = await async_client.get(
            f"{settings.API_V1_STR}/documents/99999"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_document_invalid_company(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        valid_document_data: dict
    ):
        """존재하지 않는 회사로 문서 생성 시도"""
        files = {
            'file': ('test.pdf', b'test content', 'application/pdf')
        }
        data = {
            'title': valid_document_data['title'],
            'type': valid_document_data['type'],
            'company_id': '99999'  # 존재하지 않는 회사 ID
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/documents/",
            files=files,
            data=data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
