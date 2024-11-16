# tests/conftest.py
import pytest
from typing import Generator

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