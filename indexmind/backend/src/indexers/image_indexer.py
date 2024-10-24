# indexmind/backend/src/indexers/image_indexer.py

from src.indexers.base_indexer import BaseIndexer
from src.utils.logger import logger

class ImageIndexer(BaseIndexer):
    def __init__(self):
        pass

    def index(self, file_path: str):
        # Mocked implementation
        logger.info(f"Mock indexing image file: {file_path}")
