# indexmind/backend/src/llm_models/huggingface_llm.py

from transformers import AutoTokenizer
import transformers
import torch
from src.llm_models.base_llm import BaseLLM
from src.utils.logger import logger

class HuggingFaceLLM(BaseLLM):
    def __init__(self, model_name: str):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.pipeline = transformers.pipeline(
                "text-generation",
                model=model_name,
                torch_dtype=torch.float16,
                device_map="auto",
            )

        except Exception as e:
            logger.error(f"Ошибка при загрузке модели HuggingFace: {e}")
            self.pipeline = None

    def generate(self, query: str, context: str) -> str:
        if self.pipeline is None:
            return "Модель не загружена."

        messages = [{"role": "user", "content": f"Вопрос: {query}\n\nКонтекст: {context}"}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        try:
            outputs = self.pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
            return outputs[0]["generated_text"]
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа через HuggingFace: {e}")
            return "Извините, не удалось получить ответ."
