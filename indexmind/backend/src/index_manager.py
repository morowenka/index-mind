# indexmind/backend/src/index_manager.py

import os
from src.indexers.document_indexer import DocumentIndexer
from src.indexers.image_indexer import ImageIndexer
from src.utils.logger import logger
from schemas.file_types import DocumentFile, ImageFile

FILE_TYPES = [DocumentFile, ImageFile]

class IndexManager:
    def __init__(self):
        self.indexers = {
            'document': DocumentIndexer(),
            'image': ImageIndexer()
            # Add other indexers here if needed
        }

    def index(self, file_paths: list):
        for file_path in file_paths:
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        self._index_file(full_path)
            elif os.path.isfile(file_path):
                self._index_file(file_path)
            else:
                logger.warning(f"Path {file_path} is not a valid file or directory")

    def _index_file(self, file_path: str):
        file_extension = os.path.splitext(file_path)[1].lower()
        for file_type_class in FILE_TYPES:
            if file_type_class.matches_extension(file_extension):
                indexer_key = file_type_class.indexer_key
                if indexer := self.indexers.get(indexer_key):
                    try:
                        indexer.index(file_path)
                    except PermissionError as e:
                        logger.error(f"Permission denied for file {file_path}: {e}")
                    return