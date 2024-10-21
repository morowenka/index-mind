from haystack.document_store.faiss import FAISSDocumentStore
from haystack.nodes import DensePassageRetriever, PreProcessor
from tqdm import tqdm


class DocumentIndexer:
    def __init__(self):
        self.document_store = FAISSDocumentStore(faiss_index_factory_str="Flat")
        self.retriever = DensePassageRetriever(
            document_store=self.document_store,
            query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
            passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
        )
    
    def index_documents(self, documents):
        """
        Индексирует список документов.
        
        :param documents: Список словарей вида {"content": "текст документа", "meta": {...}}
        """
        preprocessor = PreProcessor(
            split_by="word",
            split_length=200,
            split_overlap=20,
            clean_empty_lines=True,
            clean_whitespace=True,
            split_respect_sentence_boundary=True,
        )
        
        processed_docs = preprocessor.process(documents)
        
        self.document_store.write_documents(processed_docs)
    
    def update_faiss(self):
        """Обновляет индекс FAISS после добавления новых документов."""
        self.document_store.update_embeddings(self.retriever)


if __name__ == "__main__":
    documents = [
      {"content": "Текст первого документа", "meta": {"name": "doc_1"}},
      {"content": "Текст второго документа", "meta": {"name": "doc_2"}}
    ]
    
    indexer = DocumentIndexer()
    indexer.index_documents(documents)
    indexer.update_faiss()