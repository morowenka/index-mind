# indexmind/backend/src/retrievers/document_retriever.py

from src.retrievers.base_retriever import BaseRetriever
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from config import settings
from src.utils.logger import logger
import os
# TODO: replace FAISS to pinecone

# Initialize the document store and retriever at the module level
faiss_index_path = settings.DOCUMENT_FAISS_INDEX_PATH
faiss_config_path = settings.DOCUMENT_FAISS_CONFIG_PATH
sql_url = settings.DOCUMENT_SQL_DATABASE_URL

def initialize_document_store(faiss_index_path, faiss_config_path, sql_url):
    if os.path.exists(faiss_index_path) and os.path.exists(faiss_config_path):
        logger.debug(f"Loading existing FAISS index from {faiss_index_path}, config from {faiss_config_path} and SQL database from {sql_url}...")
        document_store = FAISSDocumentStore(
            faiss_index_path=faiss_index_path,
            faiss_config_path=faiss_config_path
        )
        # Check for documents without embeddings
        num_documents = document_store.get_document_count()
        num_embeddings = document_store.get_embedding_count()
        if num_documents != num_embeddings:
            logger.warning(f"There are {num_documents - num_embeddings} documents without embeddings.")
    else:
        logger.debug("Creating new FAISS index and SQL database...")
        document_store = FAISSDocumentStore(
            faiss_index_factory_str=settings.FAISS_INDEX_FACTORY_STR,
            embedding_dim=settings.RETRIEVER_EMBEDDINGS_DIM,
            sql_url=sql_url,
            duplicate_documents=settings.DOC_INDEXER_DUPLICATE_DOCUMENTS_POLICY,
            progress_bar=settings.DOC_INDEXER_DUPLICATE_PROGRESS_BAR,
            batch_size=settings.DOC_INDEXER_UPDATE_EMBEDDINGS_BATCH_SIZE,
            similarity=settings.RETRIEVER_SIMILARITY,
            validate_index_sync=settings.DOC_INDEXER_VALIDATE_INDEX_SYNC
        )
    return document_store

document_store = initialize_document_store(
    faiss_index_path=settings.DOCUMENT_FAISS_INDEX_PATH,
    faiss_config_path=settings.DOCUMENT_FAISS_CONFIG_PATH,
    sql_url=settings.DOCUMENT_SQL_DATABASE_URL
)

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model=settings.RETRIEVER_EMBEDDINGS_MODEL,
    model_format=settings.RETRIEVER_MODEL_FORMAT,
    use_gpu=settings.USE_GPU and settings.RETRIEVER_USE_GPU,
    api_key=settings.RETRIEVER_API_KEY,
    api_base=settings.RETRIEVER_API_BASE,
    query_prompt=settings.RETRIEVER_QUERY_PROMPT,
    batch_size=settings.RETRIEVER_BATCH_SIZE,
    top_k=settings.RETRIEVER_TOP_K,
    progress_bar=settings.RETRIEVER_PROGRESS_BAR,
    devices=settings.RETRIEVER_DEVICES,
    scale_score=settings.RETRIEVER_SCALE_SCORE,
    max_seq_len=settings.RETRIEVER_MAX_SEQ_LEN
)


class DocumentRetriever(BaseRetriever):
    def __init__(self):
        self.document_store = document_store
        self.retriever = retriever

    def retrieve(self, query: str, top_k: int = 5, filters: dict = None):
        """
        Retrieves documents based on a given query, returning the top results.
        
        Args:
            query (str): The search query used to retrieve documents.
            top_k (int, optional): The number of top results to return. Defaults to 5.
            filters (dict, optional): A dictionary of filters to apply during retrieval. Defaults to None.

        Returns:
            list: A list of retrieved documents.

        Raises:
            None: This function does not raise any exceptions, but logs errors if retrieval fails.
        """

        logger.debug(f"Retrieving for query: '{query}' with top_k={top_k} and filters={filters}")
        # Prefix the query for E5 model
        query = f"query: {query}"

        results = self.retriever.retrieve(query=query, top_k=top_k, filters=filters)
        logger.debug(f"Retrieved {len(results)} documents")

        # Log details of retrieved documents
        for doc in results:
            logger.debug(f"Document ID: {doc.id}, Score: {doc.score}, Content: {doc.content[:50]}, Meta: {doc.meta}")

        return results
