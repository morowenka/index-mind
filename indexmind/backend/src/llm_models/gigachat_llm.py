from langchain_community.chat_models.gigachat import GigaChat
from src.llm_models.base_llm import BaseLLM
from src.utils.logger import logger
import os
from dotenv import load_dotenv
from config.app import settings

class GigaChatLLM(BaseLLM):
    def __init__(self, model_name: str = "GigaChat"):
        """
        Инициализация GigaChat через LangChain.
        """
        try:
            giga_key = settings.SB_AUTH_DATA
            if not giga_key:
                raise ValueError("Отсутствует ключ SB_AUTH_DATA для GigaChat API.")

            self.giga_chat = GigaChat(
                credentials=giga_key, model=model_name, timeout=30, verify_ssl_certs=False
            )
            logger.info(f"Модель GigaChat '{model_name}' успешно инициализирована.")
        except Exception as e:
            logger.error(f"Ошибка инициализации GigaChat: {e}")
            self.giga_chat = None

    def generate(self, query: str, context: str) -> str:
        """
        Генерация текста с использованием GigaChat.
        """
        if self.giga_chat is None:
            return "GigaChat не инициализирован."

        try:
            prompt = f"Вопрос: {query}\n\nКонтекст: {context}"
            logger.info(f"Отправка запроса в GigaChat с промптом: {prompt}")
            response = self.giga_chat.predict(text=prompt)
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации через GigaChat: {e}")
            return "Извините, не удалось получить ответ от GigaChat."
