# indexmind/backend/src/retrievers/document_retriever.py

from src.retrievers.base_retriever import BaseRetriever
from src.stores.document_store import get_document_store
from src.embedders.document_embedder import get_document_embedder
from src.utils.logger import logger
from haystack import Document
from typing import List
from haystack_integrations.components.retrievers.pinecone import PineconeEmbeddingRetriever

class DocumentRetriever(BaseRetriever):
    def __init__(self):
        self.document_store = get_document_store()
        self.retriever = PineconeEmbeddingRetriever(
            document_store=self.document_store
        )

    def retrieve(self, query_embedding: List[float], top_k: int = 5, filters: dict = None):
        retrieved_documents = self.retriever.run(query_embedding=query_embedding, top_k=top_k, filters=filters)['documents']
        logger.info(f"Ретрив завершен, найдено {len(retrieved_documents)} документов.")
        return retrieved_documents
