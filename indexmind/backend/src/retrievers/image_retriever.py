from src.retrievers.base_retriever import BaseRetriever


class ImageRetriever(BaseRetriever):
    def retrieve(self, query: str, top_k: int = 5):
        # Mocked implementation
        return []
