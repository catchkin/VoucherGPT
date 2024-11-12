import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import os
from pathlib import Path
from typing import Dict, AsyncGenerator

from app.core.config import settings
from app.models.document import Document, DocumentType
from app.crud import crud_document, document
from app.schemas.document import DocumentCreate

pytestmark = pytest.mark.asyncio

# 기본 CRUD 테스트
async def test_create_document(
        client: AsyncClient,
        session: AsyncSession
) -> None:
    """문서 메타데이터 생성 테스트"""
    document_in = {
        "title": "Test Document",
        "type": "business_plan",  # Enum value를 소문자로 직접 전달
        "content": "Test content"
    }

    print(f"\nSending request with data: {document_in}")

    response = await client.post(
        "/api/v1/documents/",
        json=document_in
    )

    # 응답 내용 자세히 출력
    print(f"\nResponse status: {response.status_code}")
    try:
        print(f"Response content: {response.json()}")
    except:
        print(f"Raw response content: {response.content}")

    assert response.status_code == 201
    content = response.json()
    assert content["title"] == document_in["title"]
    assert content["type"] == "business_plan"  # 소문자 값으로 비교
    assert "id" in content

