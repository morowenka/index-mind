# indexmind/backend/src/search_engine.py

from src.retrievers.document_retriever import DocumentRetriever
from src.utils.logger import logger

class SearchEngine:
    def __init__(self):
        self.document_retriever = DocumentRetriever()

    def search(self, query: str, n: int = 5, filters: dict = None):
        # if filters is None:
        #     filters = {}
        # filters['status'] = ['ready']
        logger.debug(f"SearchEngine.search called with query: '{query}', n: {n}, filters: {filters}")
        logger.debug(f"Total documents in document_store: {self.document_retriever.document_store.count_documents()}")

        retrieved_documents = self.document_retriever.retrieve(query, top_k=n, filters=filters)
        
        formatted_retrieved_documents = []
        for document in retrieved_documents:
            formatted_document = {
                'id': document.id,
                'content': document.content,
                'metadata': {
                    **document.meta
                },
                'score': float(document.score)
            }
            formatted_retrieved_documents.append(formatted_document)

        logger.debug(f"Formatted results: {formatted_retrieved_documents}")
        return formatted_retrieved_documents
