# /config/app.py

from pydantic import BaseSettings
import logging
from typing import List, Optional, Literal

class LoggerConfig(BaseSettings):
    LOGGING_LEVEL: int = logging.DEBUG

class AppConfig(BaseSettings):
    USE_GPU: bool = False
    
    
class DocumentStoreConfig(BaseSettings):
    DOCUMENT_STORE_EMBEDDINGS_DIM: int = 1024
    DOCUMENT_STORE_BATCH_SIZE: int = 32
    DOCUMENT_STORE_SIMILARITY: Literal['cosine', 'euclidean', 'dotproduct'] = "cosine"
    
class DocumentEmbedderConfig(BaseSettings):
    DOC_EMBEDDER_PRECISION: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = "float32"
    DOC_EMBEDDER_PROGRESS_BAR: bool = True
    DOC_EMBEDDER_BATCH_SIZE: int = 32
    DOC_EMBEDDER_MODEL: str = "intfloat/multilingual-e5-large-instruct"

class DocumentRetrieverConfig(BaseSettings):
    RETRIEVER_QUERY_PROMPT: Optional[str] = "Choose the most relevant data"
    RETRIEVER_TOP_K: int = 10

class DocumentIndexerConfig(BaseSettings):
    DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH: int = 300
    DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP: int = 20
    DOC_INDEXER_PREPROCESSOR_CLEAN_EMPTY_LINES: bool = False
    DOC_INDEXER_PREPROCESSOR_CLEAN_WHITESPACE: bool = False
    DOC_INDEXER_PREPROCESSOR_PROGRESS_BAR: bool = False
    DOC_INDEXER_UPDATE_EMBEDDINGS_BATCH_SIZE: int = 100
    DOC_INDEXER_VALIDATE_INDEX_SYNC: bool = False

class PineconeConfig(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_CLOUD: str
    PINECONE_REGION: str
    PINECONE_HOST: str
    PINECONE_PROJECT_NAME: str
    PINECONE_INDEX_NAME: str

class Settings(
    LoggerConfig,
    AppConfig,
    DocumentRetrieverConfig,
    DocumentIndexerConfig,
    PineconeConfig,
    DocumentStoreConfig,
    DocumentEmbedderConfig
):
    class Config:
        env_file = ".env"

settings = Settings()
