# /config/app.py

from pydantic import BaseSettings
import logging
from typing import List

class LoggerConfig(BaseSettings):
    LOGGING_LEVEL: int = logging.DEBUG

class AppConfig(BaseSettings):
    USE_GPU: bool = False

class DocumentRetrieverConfig(BaseSettings):
    RETRIEVER_EMBEDDINGS_MODEL: str = "intfloat/multilingual-e5-large-instruct"
    RETRIEVER_EMBEDDINGS_DIM: int = 1024  # Adjust if necessary
    RETRIEVER_MODEL_FORMAT: str = "sentence_transformers"
    RETRIEVER_USE_GPU: bool = True
    RETRIEVER_API_KEY: str | None = None
    RETRIEVER_API_BASE: str | None = None
    RETRIEVER_QUERY_PROMPT: str | None = None
    RETRIEVER_BATCH_SIZE: int = 32
    RETRIEVER_TOP_K: int = 10
    RETRIEVER_PROGRESS_BAR: bool = False
    RETRIEVER_DEVICES: List | None = None
    RETRIEVER_SCALE_SCORE: bool = False
    RETRIEVER_MAX_SEQ_LEN: int = 512
    RETRIEVER_SIMILARITY: str = "dot_product"


class DocumentIndexerConfig(BaseSettings):
    DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH: int = 300
    DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP: int = 20
    DOC_INDEXER_PREPROCESSOR_CLEAN_EMPTY_LINES: bool = False
    DOC_INDEXER_PREPROCESSOR_CLEAN_WHITESPACE: bool = False
    DOC_INDEXER_PREPROCESSOR_PROGRESS_BAR: bool = False
    DOC_INDEXER_UPDATE_EMBEDDINGS_BATCH_SIZE: int = 100
    DOC_INDEXER_DUPLICATE_DOCUMENTS_POLICY: str = "overwrite"
    DOC_INDEXER_DUPLICATE_PROGRESS_BAR: bool = False
    DOC_INDEXER_DUPLICATE_PROGRESS_BAR: bool = False
    DOC_INDEXER_VALIDATE_INDEX_SYNC: bool = False

class FaissConfig(BaseSettings):
    FAISS_INDEX_FACTORY_STR: str = "Flat"
    DOCUMENT_FAISS_INDEX_PATH: str = "./data/document_store_index.faiss"
    DOCUMENT_FAISS_CONFIG_PATH: str = "./data/document_store_index.json" # = DOCUMENT_FAISS_INDEX_PATH with replace .faiss on .json
    DOCUMENT_SQL_DATABASE_URL: str = "sqlite:///data/document_store.db"


class Settings(
    LoggerConfig,
    AppConfig,
    DocumentRetrieverConfig,
    DocumentIndexerConfig,
    FaissConfig
):
    class Config:
        env_file = ".env"

settings = Settings()
