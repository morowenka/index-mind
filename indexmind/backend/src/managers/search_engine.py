# indexmind/backend/src/managers/search_engine.py

from src.retrievers.document_retriever import DocumentRetriever
from src.managers.llm_manager import llm_manager
from src.utils.logger import logger
from src.embedders.text_embedder import get_text_embedder

        
class SearchEngine:
    def __init__(self):
        self.document_retriever = DocumentRetriever()
        self.llm_manager = llm_manager  # Используем singleton-инстанс
        self.text_embedder = get_text_embedder()

    def search(self, query: str, n: int = 5, filters: dict = None):
        logger.info(f"Начало поиска по запросу: '{query}'")
        query_embedding = self.text_embedder.run(query)['embedding']
        retrieved_documents = self.document_retriever.retrieve(query_embedding, top_k=n, filters=filters)

        formatted_retrieved_documents = []
        for document in retrieved_documents:
            formatted_document = {
                'id': document.id,
                'content': document.content,
                'metadata': document.meta,
                'score': float(document.score) if document.score else None
            }
            formatted_retrieved_documents.append(formatted_document)

        logger.info(f"Найдено {len(formatted_retrieved_documents)} документов. Генерация ответа с помощью LLM.")
        # Используем LLM для генерации ответа на основе запроса и найденных документов
        response = self.llm_manager.generate_answer(query, retrieved_documents)
        logger.info(f"Сгенерированный ответ: '{response}'")

        return response, formatted_retrieved_documents
