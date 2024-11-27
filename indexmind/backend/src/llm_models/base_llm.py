# indexmind/backend/src/llm_models/base_llm.py

from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, query: str, context: str) -> str:
        pass
