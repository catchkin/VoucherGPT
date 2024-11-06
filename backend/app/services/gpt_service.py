from openai import OpenAI
from backend.app.core.config import settings

class GPTService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.MODEL_NAME

    async def generate_plan_content(
            self,
            section_type: str,
            company_data: dict,
            reference_text: str = None
    ) -> str:
        try:
            prompt = self._create_prompt(section_type, company_data, reference_text)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in writing export voucher business plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"GPT 내용 생성 실패: {str(e)}")

    def _create_prompt(self, section_type: str, company_data: dict, reference_text: str = None) -> str:
        prompt = f"""
        아래 정보를 바탕으로 수출바우처 사업계획서의 {section_type} 섹션을 작성해주세요.
    
        회사 정보:
        {company_data}
        """

        if reference_text:
            prompt += f"\n참고 자료:\n{reference_text}"

        return prompt