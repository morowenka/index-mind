# indexmind/backend/src/embedders/document_embedder.py

from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from config import settings

_document_embedder = None

def get_document_embedder():
    global _document_embedder
    if _document_embedder is None:
        _document_embedder = SentenceTransformersDocumentEmbedder(
            model=settings.DOC_EMBEDDER_MODEL,
            precision=settings.DOC_EMBEDDER_PRECISION,
            batch_size=settings.DOC_EMBEDDER_BATCH_SIZE,
            progress_bar=settings.DOC_EMBEDDER_PROGRESS_BAR
        )
        _document_embedder.warm_up()
    return _document_embedder
