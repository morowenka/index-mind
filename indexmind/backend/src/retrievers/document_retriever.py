# indexmind/backend/src/retrievers/document_retriever.py

from src.retrievers.base_retriever import BaseRetriever
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from config import settings
from src.utils.logger import logger
import os

# Initialize the document store and retriever at the module level
faiss_index_path = settings.DOCUMENT_FAISS_INDEX_PATH
faiss_config_path = settings.DOCUMENT_FAISS_CONFIG_PATH
sql_url = settings.DOCUMENT_SQL_DATABASE_URL

if os.path.exists(faiss_index_path) and os.path.exists(faiss_config_path):
    # Load existing FAISS index and SQL database
    logger.debug("Loading existing FAISS index and SQL database...")
    document_store = FAISSDocumentStore(
        faiss_index_path=faiss_index_path,
        faiss_config_path=faiss_config_path
    )
else:
    # Create a new FAISS index and SQL database
    logger.debug("Creating new FAISS index and SQL database...")
    document_store = FAISSDocumentStore(
        faiss_index_factory_str=settings.FAISS_INDEX_FACTORY_STR,
        embedding_dim=settings.RETRIEVER_EMBEDDINGS_DIM,
        sql_url=sql_url
    )

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model=settings.RETRIEVER_EMBEDDINGS_MODEL,
    model_format=settings.RETRIEVER_MODEL_FORMAT,
    use_gpu=settings.USE_GPU and settings.RETRIEVER_USE_GPU
)

# If creating a new index, update embeddings
if not os.path.exists(faiss_index_path):
    logger.debug("Updating embeddings for the new index...")
    document_store.update_embeddings(retriever)
    document_store.save(index_path=faiss_index_path)
else:
    logger.debug("FAISS index already exists. Skipping embedding update.")


class DocumentRetriever(BaseRetriever):
    def __init__(self):
        self.document_store = document_store
        self.retriever = retriever

    def retrieve(self, query: str, top_k: int = 5, filters: dict = None):
        logger.debug(f"Retrieving for query: '{query}' with top_k={top_k} and filters={filters}")
        # Prefix the query for E5 model
        query = f"query: {query}"

        results = self.retriever.retrieve(query=query, top_k=top_k, filters=filters)
        logger.debug(f"Retrieved {len(results)} documents")

        # Log details of retrieved documents
        for doc in results:
            logger.debug(f"Document ID: {doc.id}, Score: {doc.score}, Content: {doc.content[:50]}, Meta: {doc.meta}")

        return results
