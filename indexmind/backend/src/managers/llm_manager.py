# indexmind/backend/src/managers/llm_manager.py

from src.utils.logger import logger
from src.llm_models.base_llm import BaseLLM
from src.llm_models.openai_llm import OpenAI_LLM
from src.llm_models.huggingface_llm import HuggingFaceLLM
from src.llm_models.gigachat_llm import GigaChatLLM
from config.app import settings
from typing import List
from haystack import Document
from threading import Lock
import os
from pydantic import BaseSettings
from typing import Literal


class LLMManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LLMManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._model_type = settings.LLM_MODEL_TYPE
        self._load_model(self._model_type)
        self._initialized = True

    def _load_model(self, model_type: str):
        logger.info(f"Загрузка LLM модели типа '{model_type}'")
        try:
            if model_type == "openai":
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY не установлен в настройках.")
                self._model = OpenAI_LLM(api_key=settings.OPENAI_API_KEY)
            elif model_type == "huggingface":
                self._model = HuggingFaceLLM(model_name=settings.HF_MODEL_NAME)
            elif model_type == "gigachat":
                self._model = GigaChatLLM(model_name=settings.GIGA_MODEL_NAME)
            else:
                raise ValueError(f"Неподдерживаемый тип LLM модели: {model_type}")
        except Exception as e:
            logger.error(f"LLM модель '{model_type}' инициализирована некорректно. Будет использоваться GigaChat.")
            self._model = GigaChatLLM(model_name=settings.GIGA_MODEL_NAME)
            
        self._model_type = model_type
        logger.info(f"LLM модель '{model_type}' успешно загружена.")

    def set_model_type(self, model_type: str):
        with self._lock:
            if model_type == self._model_type:
                logger.info(f"LLM модель типа '{model_type}' уже установлена.")
                return
            self._load_model(model_type)
            # Обновляем настройки
            settings.LLM_MODEL_TYPE = model_type
            # Если требуется, можно сохранить изменение в .env файле
            self._save_model_type_to_env(model_type)
            logger.info(f"Тип LLM модели обновлен на '{model_type}'.")

    def _save_model_type_to_env(self, model_type: str):
        """
        Сохраняет тип модели в файл .env.
        Предполагается, что файл .env существует и доступен для записи.
        """
        env_file = settings.__config__.env_file
        if not env_file:
            logger.warning("Файл .env не задан в настройках. Изменения не будут сохранены.")
            return
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
            with open(env_file, 'w') as f:
                found = False
                for line in lines:
                    if line.startswith("LLM_MODEL_TYPE"):
                        f.write(f"LLM_MODEL_TYPE={model_type}\n")
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f"\nLLM_MODEL_TYPE={model_type}\n")
            logger.info(f"Тип LLM модели сохранен в файл {env_file}.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении типа LLM модели в файл .env: {e}")

    def generate_answer(self, query: str, documents: List[Document]) -> str:
        context = self._prepare_context(documents)
        return self._model.generate(query, context)

    def _prepare_context(self, documents: List[Document]) -> str:
        return "\n\n".join([doc.content for doc in documents])

llm_manager = LLMManager()
