from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from openai import AsyncOpenAI

from app.models.chat import ChatHistory, ChatReference

from app.core.config import settings
from app.crud import crud_company
from app.models import Company, Document
from app.services.document_service import DocumentService

import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
        self.client = AsyncOpenAI()

    async def generate_response(
        self,
        company_id: int,
        query: str,
        db: AsyncSession
    ) -> str:
        # 1. 회사 데이터 조회
        company = await crud_company.get_with_relations(db, id=company_id)

        # 2. 관련 문서 검색
        relevant_docs = await self.document_service.search_relevant_documents(
            db,
            company_id=company_id,
            query=query
        )

        # 3. 컨텍스트 구성
        context = self._build_context(company, relevant_docs)

        # 4. GPT 응답 생성
        response = await self._generate_gpt_response(query, context)

        return response

    def _build_context(self, company: Company, documents: List[Document]) -> str:
        # 컨텍스트 구성 로직
        context = f"""
        회사정보:
        - 회사명: {company.name}
        - 주력제품: {company.product_categories}
        - 수출국가: {', '.join(company.export_countries)}
        - 목표시장: {', '.join(company.target_markets)}
        
        관련 문서 정보:
        """

        for doc in documents:
            context += f"\n{doc.content}\n"

        return context

    async def _generate_gpt_response(
        self,
        query: str,
        context: str,
        max_retries: int = 2
    ) -> str:
        """
        GPT를 사용하여 사용자 질의에 대한 응답 생성

        Args:
            query: 사용자 질문
            context: 관련 문서와 회사 정보가 포함된 컨텍스트
            max_retries: 최대 재시도 횟수

         Returns:
             생성된 응답 텍스트
        """
        # 시스템 프롬프트 구성
        system_prompt = """
        당신은 수출바우처 사업계획서 작성을 돕는 전문가입니다.
        주어진 회사 정보와 관련 문서들을 참고하여 최적의 사업계획서 내용을 제안해 주세요.
        
        응답 시 다음 사항을 준수해 주세요:
        1. 제공된 회사 정보와 문서 내용을 기반으로 구체적이고 실질적인 내용을 작성하세요.
        2. 일반적인 내용보다는 해당 기업의 특성을 반영한 맞춤형 내용을 제시하세요.
        3. 가능한 한 구체적인 수치와 데이터를 포함하여 응답하세요.
        4. 응답은 명확한 구조와 논리적인 흐름을 가져야 합니다.
        5. 필요한 경우, 추가 정보나 보완이 필요한 부분을 명시하세요.                
        """

        # 사용자 프롬프트 구성
        user_prompt = f"""
        참고 정보:
        {context}

        질문:
        {query}
        """

        # 프롬프트 템플릿 (질문 유형별 특화)
        templates = {
            "진출시장": """
            다음 형식으로 답변해주세요:

            1. 진출 희망 시장: [시장명]
            2. 선정 근거:
               - 시장 규모 및 성장성
               - 현지 시장 특성
               - 경쟁 현황
            3. 진출 전략:
               - 주요 타겟 고객
               - 진입 방식
               - 예상 경쟁우위
            """,
            "선정사유": """
            다음 요소들을 포함하여 답변해주세요:

            1. 시장 관련:
               - 시장 규모
               - 성장률
               - 주요 트렌드
            2. 제품 관련:
               - 제품 경쟁력
               - 차별화 요소
               - 현지 적합성
            3. 사업 타당성:
               - 진출 준비도
               - 예상 성과
               - 리스크 요소
            """
        }

        # 질문 유형 감지 및 템플릿 선택
        template = None
        for key, value in templates.items():
            if key in query:
                template = value
                break

        if template:
            user_prompt += f"\n{template}"

        try:
            for attempt in range(max_retries + 1):
                try:
                    response = await self.client.chat.completions.create(
                        model=settings.GPT_MODEL,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500,
                        top_p=0.9,
                        frequency_penalty=0.3,
                        presence_penalty=0.3
                    )

                    generated_text = response.choices[0].message.content

                    # 응답 검증
                    if self._validate_response(generated_text, query):
                        return self._format_response(generated_text)
                    elif attempt < max_retries:
                        continue
                    else:
                        return self._generate_fallback_response(query)

                except Exception as e:
                    if attempt < max_retries:
                        await asyncio.sleep(1)  # 재시도 전 대기
                        continue
                    else:
                        logger.error(f"Error generating GPT response: {str(e)}")
                        return self._generate_fallback_response(query)

        except Exception as e:
            logger.error(f"Critical error in GPT response generation: {str(e)}")
            return self._generate_fallback_response(query)

    def _validate_response(self, response: str, query: str) -> bool:
        """
        생성된 응답의 유효성 검증
        """
        if not response or len(response.strip()) < 50:
            return False

        # 필수 키워드 포함 여부 확인
        required_keywords = {
            "진출시장": ["시장", "규모", "성장"],
            "선정사유": ["시장", "제품", "경쟁력"],
        }

        for key, keywords in required_keywords.items():
            if key in query:
                if not all(keyword in response for keyword in keywords):
                    return False

        return True

    def _format_response(self, response: str) -> str:
        """
        응답 텍스트 포맷팅
        """
        # 불필요한 공백 제거
        response = "\n".join(line.strip() for line in response.split("\n") if line.strip())

        # 마크다운 스타일 적용
        if not response.startswith("#"):
            response = "## 답변\n\n" + response

        return response

    def _generate_fallback_response(self, query: str) -> str:
        """
        오류 상황에서의 기본 응답 생성
        """
        return f"""
        ## 답변

        죄송합니다. 현재 요청하신 내용에 대한 상세한 답변을 생성하는데 어려움이 있습니다.
        다음과 같은 정보를 추가로 제공해 주시면 더 정확한 답변이 가능합니다:

        1. 귀사의 주력 제품/서비스에 대한 상세 정보
        2. 목표 시장에 대한 구체적인 선호도
        3. 현재까지의 수출 실적이나 해외 사업 경험

        보다 구체적인 답변이 필요하시다면, 위 정보들을 포함하여 다시 문의해 주시기 바랍니다.
        """


