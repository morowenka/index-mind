import os
from pathlib import Path

BACKEND_PATH = Path(__file__).resolve().parent.parent
SRC_PATH = BACKEND_PATH / "src"


from .app import settings


settings.DOCUMENT_FAISS_INDEX_PATH = BACKEND_PATH / settings.DOCUMENT_FAISS_INDEX_PATH
settings.DOCUMENT_FAISS_CONFIG_PATH = BACKEND_PATH / settings.DOCUMENT_FAISS_CONFIG_PATH
settings.DOCUMENT_SQL_DATABASE_URL = f"sqlite:///{BACKEND_PATH / settings.DOCUMENT_SQL_DATABASE_URL.replace('sqlite:///', '')}"