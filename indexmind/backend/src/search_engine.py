# indexmind/backend/src/search_engine.py

from src.retrievers.document_retriever import DocumentRetriever
from src.utils.logger import logger

class SearchEngine:
    def __init__(self):
        self.document_retriever = DocumentRetriever()

    def search(self, query: str, n: int = 5, filters: dict = None):
        if filters is None:
            filters = {}
        filters['status'] = ['indexed']
        logger.debug(f"SearchEngine.search called with query: '{query}', n: {n}, filters: {filters}")
        logger.debug(f"Total documents in document_store: {self.document_retriever.document_store.get_document_count()}")

        results = self.document_retriever.retrieve(query, top_k=n, filters=filters)
        formatted_results = []
        for result in results:
            doc_id = result.id
            metadata = result.meta
            formatted_result = {
                'content': result.content,
                'metadata': {
                    **metadata
                },
                'score': float(result.score)
            }
            formatted_results.append(formatted_result)

        logger.debug(f"Formatted results: {formatted_results}")
        return formatted_results
