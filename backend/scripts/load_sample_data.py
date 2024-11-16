from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

from app.models.company import Company
from app.models.document import Document, DocumentType
from app.models.section import Section, SectionType

def load_samples(db_url: str):
    """샘플 데이터 로드"""
    # DB 연결
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 1. 샘플 회사 데이터
        sample_companies = [
            Company(
                name="테크스타트(주)",
                business_number="123-45-67890",
                industry="소프트웨어",
                establishment_date="2020-01-01",
                employee_count=25,
                annual_revenue=500000000,
                description="AI 기반 솔루션 전문기업",
                target_markets=["미국", "일본", "베트남"],
                export_countries=["베트남", "싱가포르"],
                export_history={
                    "2023": {"amount": 100000, "countries": ["베트남"]},
                    "2024": {"amount": 150000, "countries": ["베트남", "싱가포르"]}
                },
                is_active=True
            ),
            Company(
                name="바이오케어(주)",
                business_number="234-56-78901",
                industry="바이오헬스",
                establishment_date="2019-03-15",
                employee_count=40,
                annual_revenue=1200000000,
                description="의료기기 제조 전문기업",
                target_markets=["중국", "태국", "인도네시아"],
                export_countries=["태국"],
                export_history={
                    "2023": {"amount": 200000, "countries": ["태국"]}
                },
                is_active=True
            )
        ]

        # 회사 데이터 저장
        for company in sample_companies:
            db.add(company)
        db.flush()  # ID 생성을 위해 flush

        # 2. 샘플 문서 데이터
        sample_documents = []
        for company in sample_companies:
            # 사업계획서
            business_plan = Document(
                company_id=company.id,
                title=f"{company.name} - 수출바우처 사업계획서",
                document_type=DocumentType.BUSINESS_PLAN,
                content="수출바우처 사업계획서 상세 내용...",
                file_name="business_plan.pdf",
                mime_type="application/pdf",
                metadata={
                    "version": "1.0",
                    "author": "홍길동",
                    "created_date": "2024-01-15"
                }
            )
            sample_documents.append(business_plan)

            # 회사소개서
            company_profile = Document(
                company_id=company.id,
                title=f"{company.name} - 회사소개서",
                document_type=DocumentType.COMPANY_PROFILE,
                content="회사소개서 상세 내용...",
                file_name="company_profile.pdf",
                mime_type="application/pdf",
                metadata={
                    "version": "2.0",
                    "last_updated": "2024-02-01"
                }
            )
            sample_documents.append(company_profile)

        # 문서 데이터 저장
        for doc in sample_documents:
            db.add(doc)
        db.flush()

        # 3. 샘플 섹션 데이터
        sample_sections = []
        for doc in sample_documents:
            if doc.document_type == DocumentType.BUSINESS_PLAN:
                sections = [
                    Section(
                        document_id=doc.id,
                        company_id=doc.company_id,
                        type=SectionType.EXECUTIVE_SUMMARY,
                        title="요약",
                        content="사업 계획 요약...",
                        order=1,
                        meta_data={"importance": "high"}
                    ),
                    Section(
                        document_id=doc.id,
                        company_id=doc.company_id,
                        type=SectionType.MARKET_ANALYSIS,
                        title="시장 분석",
                        content="목표 시장 분석...",
                        order=2,
                        meta_data={"market_size": "10억 달러"}
                    ),
                    Section(
                        document_id=doc.id,
                        company_id=doc.company_id,
                        type=SectionType.BUSINESS_MODEL,
                        title="사업 모델",
                        content="수익 모델 설명...",
                        order=3,
                        meta_data={"model_type": "B2B"}
                    )
                ]
                sample_sections.extend(sections)

        # 섹션 데이터 저장
        for section in sample_sections:
            db.add(section)

        # 4. 샘플 채팅 이력
        from app.models.chat import ChatHistory, ChatReference, ChatFeedback

        sample_chats = [
            ChatHistory(
                company_id=sample_companies[0].id,
                query="희망 진출 시장 작성 부탁해",
                response="테크스타트(주)의 경우 다음과 같은 시장 진출을 추천드립니다...",
                is_bookmarked=True,
                created_at=datetime.utcnow()
            ),
            ChatHistory(
                company_id=sample_companies[1].id,
                query="선정사유 작성 부탁해",
                response="바이오케어(주)의 경우 다음과 같은 선정사유가 있습니다...",
                is_bookmarked=False,
                created_at=datetime.utcnow()
            )
        ]

        # 채팅 이력 저장
        for chat in sample_chats:
            db.add(chat)
        db.flush()

        # 채팅 참조 정보 저장
        for chat, doc in zip(sample_chats, sample_documents[:2]):
            chat_ref = ChatReference(
                chat_id=chat.id,
                document_id=doc.id,
                is_auto_referenced=True,
                relevance_score=0.85,
                created_at=datetime.utcnow()
            )
            db.add(chat_ref)

        # 채팅 피드백 저장
        feedback = ChatFeedback(
            chat_id=sample_chats[0].id,
            rating=5,
            comment="매우 도움이 되었습니다.",
            is_accurate=True,
            created_at=datetime.utcnow()
        )
        db.add(feedback)

        # 최종 커밋
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    # 테스트용 실행
    db_url = "postgresql://vouchergpt_user:blogcodi0318@localhost/vouchergpt"
    load_samples(db_url)