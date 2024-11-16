# tests/test_schemas.py
import pytest
from app.schemas import (
    CompanyCreate,
    DocumentType,
    DocumentCreate,
    SectionCreate,
    ChatHistoryCreate,
    ChatFeedbackCreate
)


def test_basic_company_info():
    """기본 회사 정보 테스트"""
    company_data = {
        "name": "테스트 기업",
        "business_number": "1234567890",  # 10자리 숫자
        "industry": "IT"
    }

    company = CompanyCreate(**company_data)

    assert company.name == "테스트 기업"
    assert company.business_number == "1234567890"
    assert company.industry == "IT"

def test_company_size_info():
    """회사 규모 정보 테스트"""
    company_data = {
        "name": "테스트 기업",
        "business_number": "1234567890",
        "employee_count": 50,
        "annual_revenue": 1000000000
    }

    company = CompanyCreate(**company_data)

    assert company.employee_count == 50
    assert company.annual_revenue == 1000000000


def test_company_dates():
    """회사 날짜 관련 정보 테스트"""
    company_data = {
        "name": "테스트 기업",
        "business_number": "1234567890",
        "establishment_date": "2020-01-01"  # YYYY-MM-DD 형식
    }

    company = CompanyCreate(**company_data)

    assert company.establishment_date == "2020-01-01"


def test_company_market_info():
    """시장 관련 정보 테스트"""
    company_data = {
        "name": "테스트 기업",
        "business_number": "1234567890",
        "target_markets": ["국내", "해외"],
        "export_countries": ["미국", "일본", "중국"]
    }

    company = CompanyCreate(**company_data)

    assert "국내" in company.target_markets
    assert "해외" in company.target_markets
    assert len(company.export_countries) == 3
    assert "미국" in company.export_countries


def test_document_schema():
    """문서 스키마 테스트"""
    # 유효한 문서 데이터
    document_data = {
        "company_id": 1,  # DocumentCreate에 추가된 필드
        "title": "사업계획서",
        "type": "business_plan",
        "content": "테스트 내용",
        "file_name": "business_plan.pdf",
        "mime_type": "application/pdf",
        "doc_metadata": {
            "version": "1.0",
            "author": "홍길동",
            "created_date": "2024-01-15"
        }
    }

    document = DocumentCreate(**document_data)

    # 데이터가 올바르게 설정되었는지 확인
    assert document.company_id == 1
    assert document.title == "사업계획서"
    assert document.type == DocumentType.BUSINESS_PLAN
    assert document.content == "테스트 내용"
    assert document.file_name == "business_plan.pdf"
    assert document.mime_type == "application/pdf"
    assert document.doc_metadata["version"] == "1.0"
    assert document.doc_metadata["author"] == "홍길동"


def test_section_schema():
    """섹션 스키마 테스트"""
    # 유효한 섹션 데이터
    section_data = {
        "document_id": 1,
        "company_id": 1,
        "type": "executive_summary",
        "title": "사업 개요",
        "content": "본 사업계획서는...",
        "order": 1,
        "meta_data": {
            "status": "completed",
            "last_edited": "2024-01-15",
            "reviewer": "김검토"
        }
    }

    section = SectionCreate(**section_data)

    # 데이터가 올바르게 설정되었는지 확인
    assert section.document_id == 1
    assert section.company_id == 1
    assert section.type == "executive_summary"
    assert section.title == "사업 개요"
    assert section.content == "본 사업계획서는..."
    assert section.order == 1
    assert section.meta_data["status"] == "completed"
    assert section.meta_data["reviewer"] == "김검토"


def test_chat_schema():
    """채팅 관련 스키마 테스트"""
    # 채팅 이력 데이터
    chat_data = {
        "company_id": 1,
        "query": "이 기업의 주요 제품은 무엇인가요?",
        "response": "해당 기업의 주요 제품은...",
        "is_bookmarked": True
    }

    chat = ChatHistoryCreate(**chat_data)

    # 채팅 이력 데이터 확인
    assert chat.company_id == 1
    assert chat.query == "이 기업의 주요 제품은 무엇인가요?"
    assert chat.response == "해당 기업의 주요 제품은..."
    assert chat.is_bookmarked == True

    # 채팅 피드백 데이터
    feedback_data = {
        "chat_id": 1,
        "rating": 5,
        "comment": "매우 유용한 답변이었습니다.",
        "is_accurate": True,
        "needs_improvement": None
    }

    feedback = ChatFeedbackCreate(**feedback_data)

    # 피드백 데이터 확인
    assert feedback.chat_id == 1
    assert feedback.rating == 5
    assert feedback.comment == "매우 유용한 답변이었습니다."
    assert feedback.is_accurate == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])