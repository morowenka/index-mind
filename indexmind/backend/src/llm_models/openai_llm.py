# indexmind/backend/src/llm_models/openai_llm.py

import openai
from src.llm_models.base_llm import BaseLLM
from src.utils.logger import logger

class OpenAI_LLM(BaseLLM):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate(self, query: str, context: str) -> str:
        prompt = f"Вопрос: {query}\nКонтекст: {context}\nОтвет:"
        try:
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7,
            )
            answer = response.choices[0].text.strip()
            return answer
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа через OpenAI: {e}")
            return "Извините, не удалось получить ответ."

