# indexmind/backend/src/embedders/text_embedder.py

from haystack.components.embedders import SentenceTransformersTextEmbedder
from config import settings

_text_embedder = None

def get_text_embedder():
    global _text_embedder
    if _text_embedder is None:
        _text_embedder = SentenceTransformersTextEmbedder(
            model=settings.DOC_EMBEDDER_MODEL,
            precision=settings.DOC_EMBEDDER_PRECISION,
            batch_size=settings.DOC_EMBEDDER_BATCH_SIZE,
            progress_bar=settings.DOC_EMBEDDER_PROGRESS_BAR
        )
        _text_embedder.warm_up()
    return _text_embedder
