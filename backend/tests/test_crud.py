import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import company, document, section, chat_history, chat_reference, chat_feedback
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.schemas.section import SectionCreate, SectionUpdate
from app.schemas.chat import ChatHistoryCreate, ChatReferenceCreate, ChatFeedbackCreate, ChatHistoryUpdate
from app.models.document import DocumentType
from app.models.section import SectionType

@pytest.mark.asyncio
class TestCompanyCRUD:
    async def test_create_company(self, db_session: AsyncSession):
        """회사 생성 테스트"""
        print("\n=== 회사 생성 테스트 시작 ===")

        # 생성할 회사 데이터 준비
        company_data = {
            "name": "Test Company",
            "business_number": "1234567890",
            "industry": "Technology",
            "employee_count": 100,
            "description": "Test company description"
        }
        print(f"생성할 회사 데이터: {company_data}")

        # CompanyCreate 스키마로 변환
        company_in = CompanyCreate(**company_data)
        print("CompanyCreate 스키마 변환 완료")

        # 회사 생성 (crud.company 대신 company 직접 사용)
        try:
            created_company = await company.create(db_session, obj_in=company_in)
            print(f"생성된 회사 ID: {created_company.id}")
            print(f"생성된 회사 정보: {created_company.__dict__}")

        except Exception as e:
            print(f"회사 생성 중 오류 발생: {str(e)}")
            raise

        # 검증
        print("\n=== 생성된 데이터 검증 ===")
        assert created_company.name == company_data["name"], f"이름이 일치하지 않음: {created_company.name} != {company_data['name']}"
        assert created_company.business_number == company_data["business_number"], "사업자번호가 일치하지 않음"
        assert created_company.industry == company_data["industry"], "산업분류가 일치하지 않음"
        assert created_company.employee_count == company_data["employee_count"], "직원수가 일치하지 않음"

        # 데이터베이스에서 다시 조회하여 확인
        print("\n=== 데이터베이스 재조회 검증 ===")
        db_company = await company.get(db_session, id=created_company.id)
        assert db_company is not None, "데이터베이스에서 회사를 찾을 수 없음"
        assert db_company.id == created_company.id, "회사 ID가 일치하지 않음"

        print("=== 회사 생성 테스트 완료 ===")

    async def test_get_company(self, db_session: AsyncSession):
        """회사 조회 테스트"""
        print("\n=== 회사 조회 테스트 시작 ===")

        # 테스트용 회사 생성
        company_data = {
            "name": "Get Test Company",
            "business_number": "9876543210",
            "industry": "IT",
            "employee_count": 50,
            "description": "Company for get test"
        }
        print(f"테스트용 회사 생성: {company_data}")

        created_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )
        print(f"생성된 회사 ID: {created_company.id}")

        # ID로 회사 조회
        try:
            fetched_company = await company.get(db_session, id=created_company.id)
            print(f"조회된 회사 정보: {fetched_company.__dict__}")
        except Exception as e:
            print(f"회사 조회 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 조회된 데이터 검증 ===")
        assert fetched_company is not None, "회사를 찾을 수 없음"
        assert fetched_company.id == created_company.id, "회사 ID 불일치"
        assert fetched_company.name == company_data["name"], "회사명 불일치"
        assert fetched_company.business_number == company_data["business_number"], "사업자번호 불일치"
        assert fetched_company.industry == company_data["industry"], "산업분류 불일치"

        # 존재하지 않는 ID로 조회
        print("\n=== 존재하지 않는 회사 조회 테스트 ===")
        non_existent_company = await company.get(db_session, id=99999)
        assert non_existent_company is None, "존재하지 않는 회사가 조회됨"

        print("=== 회사 조회 테스트 완료 ===")

    async def test_update_company(self, db_session: AsyncSession):
        """회사 정보 수정 테스트"""
        print("\n=== 회사 수정 테스트 시작 ===")

        # 테스트용 회사 생성
        initial_data = {
            "name": "Update Test Company",
            "business_number": "1111122222",
            "industry": "Manufacturing",
            "employee_count": 200,
            "description": "Company for update test"
        }
        print(f"초기 회사 데이터: {initial_data}")

        created_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**initial_data)
        )
        print(f"생성된 회사 ID: {created_company.id}")

        # 수정할 데이터 준비
        update_data = {
            "name": "Updated Company Name",
            "industry": "IT Service",
            "employee_count": 300,
            "description": "Updated company description"
        }
        print(f"수정할 데이터: {update_data}")

        try:
            # 회사 정보 수정
            updated_company = await company.update(
                db_session,
                db_obj=created_company,
                obj_in=CompanyUpdate(**update_data)
            )
            print(f"수정된 회사 정보: {updated_company.__dict__}")
        except Exception as e:
            print(f"회사 수정 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 수정된 데이터 검증 ===")
        assert updated_company.name == update_data["name"], "회사명 수정 불일치"
        assert updated_company.industry == update_data["industry"], "산업분류 수정 불일치"
        assert updated_company.employee_count == update_data["employee_count"], "직원수 수정 불일치"
        assert updated_company.description == update_data["description"], "설명 수정 불일치"
        # 수정하지 않은 필드는 유지되어야 함
        assert updated_company.business_number == initial_data["business_number"], "사업자번호가 변경됨"

        print("=== 회사 수정 테스트 완료 ===")

    async def test_delete_company(self, db_session: AsyncSession):
        """회사 삭제 테스트"""
        print("\n=== 회사 삭제 테스트 시작 ===")

        # 테스트용 회사 생성
        company_data = {
            "name": "Delete Test Company",
            "business_number": "9999988888",
            "industry": "Service",
            "employee_count": 150,
            "description": "Company for delete test"
        }
        print(f"삭제할 회사 데이터: {company_data}")

        created_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )
        print(f"생성된 회사 ID: {created_company.id}")

        try:
            # 회사 삭제
            deleted_company = await company.remove(db_session, id=created_company.id)
            print(f"삭제된 회사 정보: {deleted_company.__dict__}")
        except Exception as e:
            print(f"회사 삭제 중 오류 발생: {str(e)}")
            raise

        # 삭제 검증
        print("\n=== 삭제 검증 ===")
        assert deleted_company.id == created_company.id, "삭제된 회사 ID 불일치"

        # 삭제된 회사 조회 시도
        fetched_company = await company.get(db_session, id=created_company.id)
        assert fetched_company is None, "삭제된 회사가 여전히 조회됨"

        # 존재하지 않는 회사 삭제 시도
        print("\n=== 존재하지 않는 회사 삭제 테스트 ===")
        try:
            await company.remove(db_session, id=99999)
            assert False, "존재하지 않는 회사 삭제가 성공함"
        except Exception as e:
            print(f"예상된 오류 발생: {str(e)}")

        print("=== 회사 삭제 테스트 완료 ===")

@pytest.mark.asyncio
class TestDocumentCRUD:
    async def test_create_document(self, db_session: AsyncSession):
        """문서 생성 테스트"""
        print("\n=== 문서 생성 테스트 시작 ===")

        # 테스트용 회사 먼저 생성
        company_data = {
            "name": "Document Test Company",
            "business_number": "1234567890",
            "industry": "Technology"
        }
        test_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )
        print(f"테스트용 회사 생성 완료 - ID: {test_company.id}")

        # 문서 데이터 준비
        document_data = {
            "company_id": test_company.id,
            "title": "Test Business Plan",
            "type": DocumentType.BUSINESS_PLAN,
            "content": "Test business plan content",
            "file_name": "business_plan.pdf",
            "mime_type": "application/pdf"
        }
        print(f"생성할 문서 데이터: {document_data}")

        try:
            created_document = await document.create(
                db_session,
                obj_in=DocumentCreate(**document_data)
            )
            print(f"생성된 문서 정보: {created_document.__dict__}")
        except Exception as e:
            print(f"문서 생성 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 생성된 문서 데이터 검증 ===")
        assert created_document.title == document_data["title"], "문서 제목 불일치"
        assert created_document.type == document_data["type"], "문서 타입 불일치"
        assert created_document.content == document_data["content"], "문서 내용 불일치"
        assert created_document.company_id == test_company.id, "회사 ID 불일치"

        print("=== 문서 생성 테스트 완료 ===")
        return created_document

    async def test_get_document(self, db_session: AsyncSession):
        """문서 조회 테스트"""
        print("\n=== 문서 조회 테스트 시작 ===")

        # 테스트용 회사와 문서 생성
        company_data = {
            "name": "Get Document Test Company",
            "business_number": "9876543210",
            "industry": "IT"
        }
        test_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )

        document_data = {
            "company_id": test_company.id,
            "title": "Get Test Document",
            "type": DocumentType.COMPANY_PROFILE,
            "content": "Test company profile content"
        }
        created_document = await document.create(
            db_session,
            obj_in=DocumentCreate(**document_data)
        )
        print(f"테스트용 문서 생성 완료 - ID: {created_document.id}")

        # ID로 문서 조회
        try:
            fetched_document = await document.get(db_session, id=created_document.id)
            print(f"조회된 문서 정보: {fetched_document.__dict__}")
        except Exception as e:
            print(f"문서 조회 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 조회된 문서 데이터 검증 ===")
        assert fetched_document is not None, "문서를 찾을 수 없음"
        assert fetched_document.id == created_document.id, "문서 ID 불일치"
        assert fetched_document.title == document_data["title"], "문서 제목 불일치"
        assert fetched_document.type == document_data["type"], "문서 타입 불일치"
        assert fetched_document.company_id == test_company.id, "회사 ID 불일치"

        # 회사별 문서 목록 조회
        company_documents = await document.get_by_company(
            db_session,
            company_id=test_company.id
        )
        print(f"\n회사 문서 목록 조회 결과: {len(company_documents)}개 문서 발견")
        assert len(company_documents) > 0, "회사의 문서가 조회되지 않음"

        print("=== 문서 조회 테스트 완료 ===")

    async def test_update_document(self, db_session: AsyncSession):
        """문서 수정 테스트"""
        print("\n=== 문서 수정 테스트 시작 ===")

        # 테스트용 회사와 문서 생성
        company_data = {
            "name": "Update Document Test Company",
            "business_number": "1111122222",
            "industry": "Manufacturing"
        }
        test_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )

        initial_document_data = {
            "company_id": test_company.id,
            "title": "Original Document",
            "type": DocumentType.BUSINESS_PLAN,
            "content": "Original content"
        }
        created_document = await document.create(
            db_session,
            obj_in=DocumentCreate(**initial_document_data)
        )
        print(f"테스트용 문서 생성 완료 - ID: {created_document.id}")

        # 수정할 데이터 준비
        update_data = {
            "title": "Updated Document Title",
            "type": DocumentType.PRODUCT_CATALOG,
            "content": "Updated content"
        }
        print(f"수정할 문서 데이터: {update_data}")

        try:
            updated_document = await document.update(
                db_session,
                db_obj=created_document,
                obj_in=DocumentUpdate(**update_data)
            )
            print(f"수정된 문서 정보: {updated_document.__dict__}")
        except Exception as e:
            print(f"문서 수정 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 수정된 문서 데이터 검증 ===")
        assert updated_document.title == update_data["title"], "문서 제목 수정 불일치"
        assert updated_document.type == update_data["type"], "문서 타입 수정 불일치"
        assert updated_document.content == update_data["content"], "문서 내용 수정 불일치"
        assert updated_document.company_id == test_company.id, "회사 ID가 변경됨"

        print("=== 문서 수정 테스트 완료 ===")

    async def test_delete_document(self, db_session: AsyncSession):
        """문서 삭제 테스트"""
        print("\n=== 문서 삭제 테스트 시작 ===")

        # 테스트용 회사와 문서 생성
        company_data = {
            "name": "Delete Document Test Company",
            "business_number": "9999988888",
            "industry": "Service"
        }
        test_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )

        document_data = {
            "company_id": test_company.id,
            "title": "Document to Delete",
            "type": DocumentType.TRAINING_DATA,
            "content": "Content to delete"
        }
        created_document = await document.create(
            db_session,
            obj_in=DocumentCreate(**document_data)
        )
        print(f"삭제할 문서 생성 완료 - ID: {created_document.id}")

        try:
            # 문서 삭제
            deleted_document = await document.remove(db_session, id=created_document.id)
            print(f"삭제된 문서 정보: {deleted_document.__dict__}")
        except Exception as e:
            print(f"문서 삭제 중 오류 발생: {str(e)}")
            raise

        # 삭제 검증
        print("\n=== 삭제 검증 ===")
        assert deleted_document.id == created_document.id, "삭제된 문서 ID 불일치"

        # 삭제된 문서 조회 시도
        fetched_document = await document.get(db_session, id=created_document.id)
        assert fetched_document is None, "삭제된 문서가 여전히 조회됨"

        # 회사의 문서 목록 확인
        company_documents = await document.get_by_company(
            db_session,
            company_id=test_company.id
        )
        assert created_document.id not in [doc.id for doc in company_documents], \
            "삭제된 문서가 회사 문서 목록에 여전히 존재함"

        print("=== 문서 삭제 테스트 완료 ===")

@pytest.mark.asyncio
class TestSectionCRUD:
    async def test_create_section(self, db_session: AsyncSession):
        """섹션 생성 테스트"""
        print("\n=== 섹션 생성 테스트 시작 ===")

        # 테스트용 회사 생성
        company_data = {
            "name": "Section Test Company",
            "business_number": "1234567890",
            "industry": "Technology"
        }
        test_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )
        print(f"테스트용 회사 생성 완료 - ID: {test_company.id}")

        # 테스트용 문서 생성
        document_data = {
            "company_id": test_company.id,
            "title": "Test Business Plan",
            "type": DocumentType.BUSINESS_PLAN
        }
        test_document = await document.create(
            db_session,
            obj_in=DocumentCreate(**document_data)
        )
        print(f"테스트용 문서 생성 완료 - ID: {test_document.id}")

        # 섹션 데이터 준비
        section_data = {
            "document_id": test_document.id,
            "company_id": test_company.id,
            "type": SectionType.EXECUTIVE_SUMMARY,
            "title": "Executive Summary",
            "content": "This is an executive summary section",
            "order": 1
        }
        print(f"생성할 섹션 데이터: {section_data}")

        try:
            created_section = await section.create(
                db_session,
                obj_in=SectionCreate(**section_data)
            )
            print(f"생성된 섹션 정보: {created_section.__dict__}")
        except Exception as e:
            print(f"섹션 생성 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 생성된 섹션 데이터 검증 ===")
        assert created_section.title == section_data["title"], "섹션 제목 불일치"
        assert created_section.type == section_data["type"], "섹션 타입 불일치"
        assert created_section.content == section_data["content"], "섹션 내용 불일치"
        assert created_section.document_id == test_document.id, "문서 ID 불일치"
        assert created_section.company_id == test_company.id, "회사 ID 불일치"
        assert created_section.order == section_data["order"], "섹션 순서 불일치"

        print("=== 섹션 생성 테스트 완료 ===")
        return created_section, test_document, test_company

    async def test_get_section(self, db_session: AsyncSession):
        """섹션 조회 테스트"""
        print("\n=== 섹션 조회 테스트 시작 ===")

        # 테스트 데이터 생성
        created_section, test_document, test_company = await self.test_create_section(db_session)

        # ID로 섹션 조회
        try:
            fetched_section = await section.get(db_session, id=created_section.id)
            print(f"조회된 섹션 정보: {fetched_section.__dict__}")
        except Exception as e:
            print(f"섹션 조회 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 조회된 섹션 데이터 검증 ===")
        assert fetched_section is not None, "섹션을 찾을 수 없음"
        assert fetched_section.id == created_section.id, "섹션 ID 불일치"
        assert fetched_section.document_id == test_document.id, "문서 ID 불일치"
        assert fetched_section.company_id == test_company.id, "회사 ID 불일치"

        # 문서별 섹션 목록 조회
        document_sections = await section.get_by_document(
            db_session,
            document_id=test_document.id
        )
        print(f"\n문서의 섹션 목록 조회 결과: {len(document_sections)}개 섹션 발견")
        assert len(document_sections) > 0, "문서의 섹션이 조회되지 않음"

        # 타입별 섹션 조회
        type_sections = await section.get_by_type(
            db_session,
            section_type=SectionType.EXECUTIVE_SUMMARY
        )
        print(f"\n특정 타입의 섹션 조회 결과: {len(type_sections)}개 섹션 발견")
        assert len(type_sections) > 0, "해당 타입의 섹션이 조회되지 않음"

        print("=== 섹션 조회 테스트 완료 ===")

    async def test_update_section(self, db_session: AsyncSession):
        """섹션 수정 테스트"""
        print("\n=== 섹션 수정 테스트 시작 ===")

        # 테스트 데이터 생성
        created_section, test_document, test_company = await self.test_create_section(db_session)

        # 수정할 데이터 준비
        update_data = {
            "title": "Updated Executive Summary",
            "content": "Updated executive summary content",
            "type": SectionType.EXECUTIVE_SUMMARY,
            "order": 2
        }
        print(f"수정할 섹션 데이터: {update_data}")

        try:
            updated_section = await section.update(
                db_session,
                db_obj=created_section,
                obj_in=SectionUpdate(**update_data)
            )
            print(f"수정된 섹션 정보: {updated_section.__dict__}")
        except Exception as e:
            print(f"섹션 수정 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 수정된 섹션 데이터 검증 ===")
        assert updated_section.title == update_data["title"], "섹션 제목 수정 불일치"
        assert updated_section.content == update_data["content"], "섹션 내용 수정 불일치"
        assert updated_section.order == update_data["order"], "섹션 순서 수정 불일치"
        # 변경되면 안 되는 필드 검증
        assert updated_section.document_id == test_document.id, "문서 ID가 변경됨"
        assert updated_section.company_id == test_company.id, "회사 ID가 변경됨"

        print("=== 섹션 수정 테스트 완료 ===")

    async def test_delete_section(self, db_session: AsyncSession):
        """섹션 삭제 테스트"""
        print("\n=== 섹션 삭제 테스트 시작 ===")

        # 테스트 데이터 생성
        created_section, test_document, test_company = await self.test_create_section(db_session)

        try:
            # 섹션 삭제
            deleted_section = await section.remove(db_session, id=created_section.id)
            print(f"삭제된 섹션 정보: {deleted_section.__dict__}")
        except Exception as e:
            print(f"섹션 삭제 중 오류 발생: {str(e)}")
            raise

        # 삭제 검증
        print("\n=== 삭제 검증 ===")
        assert deleted_section.id == created_section.id, "삭제된 섹션 ID 불일치"

        # 삭제된 섹션 조회 시도
        fetched_section = await section.get(db_session, id=created_section.id)
        assert fetched_section is None, "삭제된 섹션이 여전히 조회됨"

        # 문서의 섹션 목록 확인
        document_sections = await section.get_by_document(
            db_session,
            document_id=test_document.id
        )
        assert created_section.id not in [s.id for s in document_sections], \
            "삭제된 섹션이 문서 섹션 목록에 여전히 존재함"

        print("=== 섹션 삭제 테스트 완료 ===")

    async def test_reorder_sections(self, db_session: AsyncSession):
        """섹션 순서 변경 테스트"""
        print("\n=== 섹션 순서 변경 테스트 시작 ===")

        # 테스트용 회사와 문서 생성
        company_data = {
            "name": "Reorder Test Company",
            "business_number": "5555566666",
            "industry": "Service"
        }
        test_company = await company.create(
            db_session,
            obj_in=CompanyCreate(**company_data)
        )

        document_data = {
            "company_id": test_company.id,
            "title": "Test Document for Reordering",
            "type": DocumentType.BUSINESS_PLAN
        }
        test_document = await document.create(
            db_session,
            obj_in=DocumentCreate(**document_data)
        )

        # 여러 섹션 생성
        sections_data = [
            {
                "document_id": test_document.id,
                "company_id": test_company.id,
                "type": SectionType.EXECUTIVE_SUMMARY,
                "title": "Executive Summary",
                "order": 1
            },
            {
                "document_id": test_document.id,
                "company_id": test_company.id,
                "type": SectionType.MARKET_ANALYSIS,
                "title": "Market Analysis",
                "order": 2
            },
            {
                "document_id": test_document.id,
                "company_id": test_company.id,
                "type": SectionType.BUSINESS_MODEL,
                "title": "Business Model",
                "order": 3
            }
        ]

        created_sections = []
        for section_data in sections_data:
            created_section = await section.create(
                db_session,
                obj_in=SectionCreate(**section_data)
            )
            created_sections.append(created_section)

        print(f"생성된 섹션 수: {len(created_sections)}")

        # 순서 변경
        new_orders = {
            created_sections[0].id: 3,  # Executive Summary를 마지막으로
            created_sections[1].id: 1,  # Market Analysis를 처음으로
            created_sections[2].id: 2  # Business Model을 중간으로
        }
        print(f"변경할 순서: {new_orders}")

        try:
            reordered_sections = await section.reorder_sections(
                db_session,
                document_id=test_document.id,
                section_orders=new_orders
            )
            print("섹션 순서 변경 완료")
        except Exception as e:
            print(f"섹션 순서 변경 중 오류 발생: {str(e)}")
            raise

        # 순서 변경 검증
        fetched_sections = await section.get_by_document(db_session, document_id=test_document.id)
        fetched_sections = sorted(fetched_sections, key=lambda x: x.order)

        print("\n=== 변경된 순서 검증 ===")
        assert fetched_sections[0].type == SectionType.MARKET_ANALYSIS, "첫 번째 섹션 순서 불일치"
        assert fetched_sections[1].type == SectionType.BUSINESS_MODEL, "두 번째 섹션 순서 불일치"
        assert fetched_sections[2].type == SectionType.EXECUTIVE_SUMMARY, "세 번째 섹션 순서 불일치"

        print("=== 섹션 순서 변경 테스트 완료 ===")

@pytest.mark.asyncio
class TestChatCRUD:
    async def create_test_company(self, db_session: AsyncSession):
        """테스트용 회사 생성"""
        company_data = {
            "name": "Chat Test Company",
            "business_number": "1234567890",
            "industry": "Technology"
        }
        return await company.create(db_session, obj_in=CompanyCreate(**company_data))

    async def create_test_document(self, db_session: AsyncSession, company_id: int):
        """테스트용 문서 생성"""
        document_data = {
            "company_id": company_id,
            "title": "Test Document",
            "type": DocumentType.BUSINESS_PLAN,
            "content": "Test content for reference"
        }
        return await document.create(db_session, obj_in=DocumentCreate(**document_data))

    async def test_create_chat_history(self, db_session: AsyncSession):
        """채팅 이력 생성 테스트"""
        print("\n=== 채팅 이력 생성 테스트 시작 ===")

        # 테스트용 회사 생성
        test_company = await self.create_test_company(db_session)
        print(f"테스트용 회사 생성 완료 - ID: {test_company.id}")

        # 채팅 이력 데이터 준비
        chat_data = {
            "company_id": test_company.id,
            "query": "What is the company's main business?",
            "response": "The company specializes in technology solutions.",
            "is_bookmarked": False
        }
        print(f"생성할 채팅 이력 데이터: {chat_data}")

        try:
            created_chat = await chat_history.create(
                db_session,
                obj_in=ChatHistoryCreate(**chat_data)
            )
            print(f"생성된 채팅 이력: {created_chat.__dict__}")
        except Exception as e:
            print(f"채팅 이력 생성 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 생성된 채팅 이력 검증 ===")
        assert created_chat.query == chat_data["query"], "질문 내용 불일치"
        assert created_chat.response == chat_data["response"], "응답 내용 불일치"
        assert created_chat.company_id == test_company.id, "회사 ID 불일치"

        print("=== 채팅 이력 생성 테스트 완료 ===")
        return created_chat, test_company

    async def test_get_chat_history(self, db_session: AsyncSession):
        """채팅 이력 조회 테스트"""
        print("\n=== 채팅 이력 조회 테스트 시작 ===")

        # 테스트 데이터 생성
        created_chat, test_company = await self.test_create_chat_history(db_session)

        # ID로 채팅 이력 조회
        try:
            fetched_chat = await chat_history.get(db_session, id=created_chat.id)
            print(f"조회된 채팅 이력: {fetched_chat.__dict__}")
        except Exception as e:
            print(f"채팅 이력 조회 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 조회된 채팅 이력 검증 ===")
        assert fetched_chat is not None, "채팅 이력을 찾을 수 없음"
        assert fetched_chat.id == created_chat.id, "채팅 이력 ID 불일치"

        # 회사별 채팅 이력 조회
        company_chats = await chat_history.get_by_company(
            db_session,
            company_id=test_company.id
        )
        print(f"\n회사의 채팅 이력 수: {len(company_chats)}")
        assert len(company_chats) > 0, "회사의 채팅 이력이 조회되지 않음"

        print("=== 채팅 이력 조회 테스트 완료 ===")

    async def test_update_chat_history(self, db_session: AsyncSession):
        """채팅 이력 수정 테스트"""
        print("\n=== 채팅 이력 수정 테스트 시작 ===")

        # 테스트 데이터 생성
        created_chat, _ = await self.test_create_chat_history(db_session)

        # 수정할 데이터 준비
        update_data = {
            "is_bookmarked": True,
            "response": "Updated response with more details"
        }
        print(f"수정할 데이터: {update_data}")

        try:
            updated_chat = await chat_history.update(
                db_session,
                db_obj=created_chat,
                obj_in=ChatHistoryUpdate(**update_data)
            )
            print(f"수정된 채팅 이력: {updated_chat.__dict__}")
        except Exception as e:
            print(f"채팅 이력 수정 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 수정된 채팅 이력 검증 ===")
        assert updated_chat.is_bookmarked == True, "북마크 상태 수정 불일치"
        assert updated_chat.response == update_data["response"], "응답 내용 수정 불일치"

        print("=== 채팅 이력 수정 테스트 완료 ===")

    async def test_create_chat_reference(self, db_session: AsyncSession):
        """채팅 참조 생성 테스트"""
        print("\n=== 채팅 참조 생성 테스트 시작 ===")

        # 테스트 데이터 생성
        created_chat, test_company = await self.test_create_chat_history(db_session)
        test_document = await self.create_test_document(db_session, test_company.id)

        # 채팅 참조 데이터 준비
        reference_data = {
            "chat_id": created_chat.id,
            "document_id": test_document.id,
            "is_auto_referenced": True,
            "relevance_score": 0.85
        }
        print(f"생성할 채팅 참조 데이터: {reference_data}")

        try:
            created_reference = await chat_reference.create(
                db_session,
                obj_in=ChatReferenceCreate(**reference_data)
            )
            print(f"생성된 채팅 참조: {created_reference.__dict__}")
        except Exception as e:
            print(f"채팅 참조 생성 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 생성된 채팅 참조 검증 ===")
        assert created_reference.chat_id == created_chat.id, "채팅 ID 불일치"
        assert created_reference.document_id == test_document.id, "문서 ID 불일치"
        assert created_reference.relevance_score == reference_data["relevance_score"], "관련성 점수 불일치"

        print("=== 채팅 참조 생성 테스트 완료 ===")
        return created_reference

    async def test_create_chat_feedback(self, db_session: AsyncSession):
        """채팅 피드백 생성 테스트"""
        print("\n=== 채팅 피드백 생성 테스트 시작 ===")

        # 테스트 데이터 생성
        created_chat, _ = await self.test_create_chat_history(db_session)

        # 피드백 데이터 준비
        feedback_data = {
            "chat_id": created_chat.id,
            "rating": 5,
            "comment": "Very helpful response",
            "is_accurate": True,
            "needs_improvement": None
        }
        print(f"생성할 채팅 피드백 데이터: {feedback_data}")

        try:
            created_feedback = await chat_feedback.create(
                db_session,
                obj_in=ChatFeedbackCreate(**feedback_data)
            )
            print(f"생성된 채팅 피드백: {created_feedback.__dict__}")
        except Exception as e:
            print(f"채팅 피드백 생성 중 오류 발생: {str(e)}")
            raise

        # 데이터 검증
        print("\n=== 생성된 채팅 피드백 검증 ===")
        assert created_feedback.chat_id == created_chat.id, "채팅 ID 불일치"
        assert created_feedback.rating == feedback_data["rating"], "평점 불일치"
        assert created_feedback.is_accurate == feedback_data["is_accurate"], "정확도 불일치"

        print("=== 채팅 피드백 생성 테스트 완료 ===")

    async def test_get_chat_feedback(self, db_session: AsyncSession):
        """채팅 피드백 조회 테스트"""
        print("\n=== 채팅 피드백 조회 테스트 시작 ===")

        # 먼저 피드백 생성
        await self.test_create_chat_feedback(db_session)

        # 긍정적인 피드백 조회
        try:
            positive_feedbacks = await chat_feedback.get_positive_feedback(
                db_session,
                min_rating=4
            )
            print(f"긍정적 피드백 수: {len(positive_feedbacks)}")
            assert len(positive_feedbacks) > 0, "긍정적 피드백이 조회되지 않음"
        except Exception as e:
            print(f"피드백 조회 중 오류 발생: {str(e)}")
            raise

        print("=== 채팅 피드백 조회 테스트 완료 ===")

    async def test_delete_chat_history(self, db_session: AsyncSession):
        """채팅 이력 삭제 테스트"""
        print("\n=== 채팅 이력 삭제 테스트 시작 ===")

        # 테스트 데이터 생성
        created_chat, _ = await self.test_create_chat_history(db_session)

        try:
            # 채팅 이력 삭제
            deleted_chat = await chat_history.remove(db_session, id=created_chat.id)
            print(f"삭제된 채팅 이력: {deleted_chat.__dict__}")
        except Exception as e:
            print(f"채팅 이력 삭제 중 오류 발생: {str(e)}")
            raise

        # 삭제 검증
        print("\n=== 삭제 검증 ===")
        fetched_chat = await chat_history.get(db_session, id=created_chat.id)
        assert fetched_chat is None, "삭제된 채팅 이력이 여전히 조회됨"

        print("=== 채팅 이력 삭제 테스트 완료 ===")