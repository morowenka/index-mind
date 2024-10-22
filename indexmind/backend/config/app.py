from pydantic import BaseSettings
import logging
    
class LoggerConfig(BaseSettings):
    LOGGING_LEVEL: int = logging.DEBUG

class AppConfig(BaseSettings):
    USE_GPU: bool = True


class DocumentRetrieverConfig(BaseSettings):
    RETRIEVER_QUERY_EMBEDDINGS_MODEL: str = "facebook/dpr-question_encoder-single-nq-base"
    RETRIEVER_PASSAGE_EMBEDDINGS_MODEL: str = "facebook/dpr-ctx_encoder-single-nq-base"
    RETRIEVER_CHUNK_SIZE: int = 300
    RETRIEVER_EMBEDDINGS_DIM: int = 768
    RETRIEVER_USE_GPU: bool = True
    
class DocumentIndexer(BaseSettings):
    DOC_INDEXER_PREPROCESSOR_SPLIT_BY: str = "word"
    DOC_INDEXER_PREPROCESSOR_SPLIT_LENGTH: int = 200
    DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP: int = 20
    DOC_INDEXER_PREPROCESSOR_CLEAN_EMPTY_LINES: bool = True
    DOC_INDEXER_PREPROCESSOR_CLEAN_WHITESPACE: bool = True
    DOC_INDEXER_PREPROCESSOR_PROGRESS_BAR: bool = False


class FaissConfig(BaseSettings):
    FAISS_INDEX_PATH: str = "./data/faiss_index"