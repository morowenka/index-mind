# indexmind/backend/src/retrievers/document_retriever.py

from src.retrievers.base_retriever import BaseRetriever
from haystack_integrations.document_stores.pinecone import PineconeDocumentStore
from haystack_integrations.components.retrievers.pinecone import PineconeEmbeddingRetriever
from config import settings
from src.utils.logger import logger
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.utils import ComponentDevice, Secret
from dotenv import load_dotenv

load_dotenv()

document_store = PineconeDocumentStore(
    api_key=Secret.from_env_var("PINECONE_API_KEY"),
    index=settings.PINECONE_INDEX_NAME,
    dimension=settings.DOCUMENT_STORE_EMBEDDINGS_DIM,
    metric=settings.DOCUMENT_STORE_SIMILARITY,
    batch_size=settings.DOCUMENT_STORE_BATCH_SIZE,
    spec={"serverless": {"region": settings.PINECONE_REGION, "cloud": settings.PINECONE_CLOUD}},
)

document_embedder = SentenceTransformersDocumentEmbedder(
    model=settings.DOC_EMBEDDER_MODEL,
    batch_size=settings.DOC_EMBEDDER_BATCH_SIZE,
    progress_bar=settings.DOC_EMBEDDER_PROGRESS_BAR,
    precision=settings.DOC_EMBEDDER_PRECISION,
    truncate_dim=settings.DOCUMENT_STORE_EMBEDDINGS_DIM
)
document_embedder.warm_up()

text_embedder = SentenceTransformersTextEmbedder(
    model=settings.DOC_EMBEDDER_MODEL,
    batch_size=settings.DOC_EMBEDDER_BATCH_SIZE,
    progress_bar=settings.DOC_EMBEDDER_PROGRESS_BAR,
    precision=settings.DOC_EMBEDDER_PRECISION,
    truncate_dim=settings.DOCUMENT_STORE_EMBEDDINGS_DIM
)
text_embedder.warm_up()

retriever = PineconeEmbeddingRetriever(
    document_store=document_store,
    top_k=settings.RETRIEVER_TOP_K,
    filters={"field": "meta.status", "operator": "==", "value": "ready"}
)

class DocumentRetriever(BaseRetriever):
    def __init__(self):
        self.document_store = document_store
        self.retriever = retriever
        self._init_pipeline()
        
    def _init_pipeline(self) -> None:
        self.pipeline = Pipeline()
        self.pipeline.add_component("text_embedder", text_embedder)
        self.pipeline.add_component("retriever", retriever)
        self.pipeline.connect("text_embedder.embedding", "retriever.query_embedding")


    def retrieve(self, query: str, top_k: int=5, filters: dict=None):
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
        retrieved_documents = self.pipeline.run(
            data={
                "retriever": {
                    "filters": filters,
                    "top_k": top_k
                },
                "text_embedder": {
                    "text": query
                }
            }
        ).get("retriever").get("documents")
        logger.debug(f"Retrieved {len(retrieved_documents)} documents")
        return retrieved_documents
