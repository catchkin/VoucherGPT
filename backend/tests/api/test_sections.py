import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.section import SectionType
from app.models.document import DocumentType

pytestmark = pytest.mark.asyncio

async def create_test_company(client: AsyncClient) -> dict:
    """테스트용 회사 생성 헬퍼 함수"""
    response = await client.post(
        f"{settings.API_V1_STR}/companies/",
        json={
            "name": "Test Company",
            "business_number": "123456789",
            "industry": "Test Industry"
        }
    )
    return response.json()



