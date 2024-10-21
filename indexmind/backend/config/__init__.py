# config/__init__.py

from .main_config import Settings


settings = Settings()

CLICKHOUSE_HOST = settings.CLICKHOUSE_HOST
CLICKHOUSE_PORT = settings.CLICKHOUSE_PORT
FAISS_INDEX_PATH = settings.FAISS_INDEX_PATH
CLICKHOUSE_DB = settings.CLICKHOUSE_DB
