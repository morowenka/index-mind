from .db import DatabaseConfig 
from .app import (
    DocumentRetrieverConfig,
    DocumentIndexer,
    LoggerConfig,
    FaissConfig,
    AppConfig
)


class Settings(
    DocumentRetrieverConfig,
    LoggerConfig,
    FaissConfig,
    DatabaseConfig,
    AppConfig,
    DocumentIndexer
):
    
     class Config:
         env_file=".env"