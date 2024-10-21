from pydantic import BaseSettings


class AppConfig(BaseSettings):
    FAISS_INDEX_PATH: str = "./data/faiss_index"