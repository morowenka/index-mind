# /config/app.py

from pydantic import BaseSettings
import logging

class LoggerConfig(BaseSettings):
    LOGGING_LEVEL: int = logging.DEBUG

class AppConfig(BaseSettings):
    USE_GPU: bool = True

class DocumentRetrieverConfig(BaseSettings):
    RETRIEVER_EMBEDDINGS_MODEL: str = "intfloat/multilingual-e5-large-instruct"
    RETRIEVER_EMBEDDINGS_DIM: int = 1024  # Adjust if necessary
    RETRIEVER_MODEL_FORMAT: str = "sentence_transformers"
    RETRIEVER_USE_GPU: bool = True


class DocumentIndexerConfig(BaseSettings):
    DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH: int = 300
    DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP: int = 20
    DOC_INDEXER_PREPROCESSOR_CLEAN_EMPTY_LINES: bool = False
    DOC_INDEXER_PREPROCESSOR_CLEAN_WHITESPACE: bool = False
    DOC_INDEXER_PREPROCESSOR_PROGRESS_BAR: bool = False

class FaissConfig(BaseSettings):
    FAISS_INDEX_FACTORY_STR: str = "Flat"
    DOCUMENT_FAISS_INDEX_PATH: str = "./data/document_faiss_index.faiss"
    DOCUMENT_FAISS_CONFIG_PATH: str = "./data/faiss_document_store.json"
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
