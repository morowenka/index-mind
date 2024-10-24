# indexmind/backend/src/search_engine.py

from src.retrievers.document_retriever import DocumentRetriever
from src.utils.logger import logger

class SearchEngine:
    def __init__(self):
        self.document_retriever = DocumentRetriever()

    def search(self, query: str, n: int = 5, filters: dict = None):
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
                    'doc_id': doc_id,
                    'file_hash': metadata.get('file_hash'),
                    'file_path': metadata.get('file_path'),
                    'start_idx': metadata.get('start_idx'),
                    'end_idx': metadata.get('end_idx'),
                    'creation_time': metadata.get('creation_time'),
                    'modification_time': metadata.get('modification_time'),
                    'type': metadata.get('type'),
                },
                'score': result.score
            }
            formatted_results.append(formatted_result)

        logger.debug(f"Formatted results: {formatted_results}")
        return formatted_results
