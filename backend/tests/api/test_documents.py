import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import os
from pathlib import Path
from typing import Dict, AsyncGenerator
from fastapi import status

from app.core.config import settings
from app.models.document import Document, DocumentType
from app.models.section import Section, SectionType
from app.models.company import Company

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

async def test_get_document(client: AsyncClient, create_document: Document):
    """특정 문서 조회 테스트"""
    response = await client.get(f"/api/v1/documents/{create_document.id}")

    assert response.status_code == 200
    content = response.json()
    assert content["id"] == create_document.id
    assert content["title"] == create_document.title

async def test_list_documents(
    client: AsyncClient,
    create_multiple_documents: list[Document]
):
    """문서 목록 조회 테스트"""
    response = await client.get("/api/v1/documents/")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content) == 3  # create_multiple_documents에서 생성한 문서 수

async def test_update_document(client: AsyncClient, create_document: Document):
    """문서 정보 수정 테스트"""
    payload = {
        "title": "Updated Document",
        "content": "Updated content"
    }
    response = await client.put(
        f"/api/v1/documents/{create_document.id}",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["title"] == payload["title"]
    assert content["content"] == payload["content"]


async def test_delete_document(
        client: AsyncClient,
        create_document: Document,
        session: AsyncSession
):
    """문서 삭제 테스트"""
    document_id = create_document.id

    # 삭제 전 문서 존재 확인
    pre_check = await client.get(f"/api/v1/documents/{document_id}")
    assert pre_check.status_code == status.HTTP_200_OK

    # 문서 삭제
    response = await client.delete(f"/api/v1/documents/{document_id}")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["id"] == document_id

    # 세션 클리어
    session.expunge_all()
    await session.commit()

    # 삭제된 문서 조회 시도
    post_check = await client.get(f"/api/v1/documents/{document_id}")
    assert post_check.status_code == status.HTTP_404_NOT_FOUND

    # DB에서 직접 확인
    from sqlalchemy import select
    query = select(Document).where(Document.id == document_id)
    result = await session.execute(query)
    assert result.scalar_one_or_none() is None


async def clear_all_tables(session: AsyncSession):
    """테스트 이후 모든 테이블 초기화"""
    try:
        # 삭제 순서 중요: 외래 키 제약 조건 고려
        await session.execute(Section.__table__.delete())
        await session.execute(Document.__table__.delete())
        await session.execute(Company.__table__.delete())
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e

@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """각 테스트 케이스 실행 전후로 테이블 초기화"""
    await clear_all_tables(session)
    yield  # 테스트 실행
    await clear_all_tables(session)