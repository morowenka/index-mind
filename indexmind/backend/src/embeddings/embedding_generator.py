from haystack.document_stores import InMemoryDocumentStore 
from haystack.nodes import DensePassageRetriever 
from haystack.schema import Document 

from config import settings
from utils.logger import logger


class DocumentEmbeddingGenerator:
    def __init__(self):
        """Инициализация InMemoryDocumentStore + Retriever"""
        self.document_store = InMemoryDocumentStore(
            embedding_dim=settings.RETRIEVER_EMBEDDINGS_DIM
        )
        self.retriever = DensePassageRetriever(
            document_store=self.document_store ,
            query_embedding_model=settings.RETRIEVER_QUERY_EMBEDDINGS_MODEL,
            passage_embedding_model=settings.RETRIEVER_PASSAGE_EMBEDDINGS_MODEL,
            use_gpu=(settings.USE_GPU & settings.RETRIEVER_USE_GPU)
        )
        self.document_store.update_embeddings(self.retriever)
          
    def add_document_with_embedding(
        self,
        content: str,
        doc_id: str,
        meta: dict = None
    ):
        """Добавление нового документа + его embedding"""
        document_to_add = [Document(content=content, id=doc_id, meta=meta)]
        try:
            self.document_store.write_documents(document_to_add)
            return True
        except Exception as e:
            logger.warning(f"Ошибка при индексации документа {doc_id}: {e}")
            return False

