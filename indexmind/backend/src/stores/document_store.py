# indexmind/backend/src/stores/document_store.py

from haystack_integrations.document_stores.pinecone import PineconeDocumentStore
from config import settings
from haystack.utils import Secret
from dotenv import load_dotenv

load_dotenv()

_document_store = None

def get_document_store():
    global _document_store
    if _document_store is None:
        _document_store = PineconeDocumentStore(
            api_key=Secret.from_env_var("PINECONE_API_KEY"),
            index=settings.PINECONE_INDEX_NAME,
            dimension=settings.DOCUMENT_STORE_EMBEDDINGS_DIM,
            metric=settings.DOCUMENT_STORE_SIMILARITY,
            batch_size=settings.DOCUMENT_STORE_BATCH_SIZE,
            spec={"serverless": {"region": settings.PINECONE_REGION, "cloud": settings.PINECONE_CLOUD}}
        )
    return _document_store
