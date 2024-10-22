import hashlib
from backend.src.db.clickhouse_client import ClickhouseClient
from backend.src.embeddings.embedding_generator import DocumentEmbeddingGenerator

from haystack.nodes import PreProcessor
from config import settings
from utils.logger import logger


def hash_file_content(file_content: str) -> str:
    """Функция вычисляет SHA256-хэш содержимого файла."""
    sha256_hash_object = hashlib.sha256(file_content.encode('utf-8'))
    return sha256_hash_object.hexdigest()


class DocumentIndexer:
    def __init__(self):
        """Инициализация клиентов"""
        self.ch_client_db = ClickhouseClient()
        self.hs_manager_db = DocumentEmbeddingGenerator()
        self.preprocessor = PreProcessor(
            split_by=settings.DOC_INDEXER_PREPROCESSOR_SPLIT_BY,
            split_length=settings.DOC_INDEXER_PREPROCESSOR_SPLIT_LENGTH,
            split_overlap=settings.DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP,
            clean_empty_lines=settings.DOC_INDEXER_PREPROCESSOR_CLEAN_EMPTY_LINES,
            clean_whitespace=settings.DOC_INDEXER_PREPROCESSOR_CLEAN_WHITESPACE,
            progress_bar=settings.DOC_INDEXER_PREPROCESSOR_PROGRESS_BAR,
        )

    def process_and_index_document(
        self,
        document_content: str,
        file_path: str
    ) -> None:
        full_file_sha256hash_value = str(hash_file_content(document_content))
        logger.debug(f"Хэш файла: {full_file_sha256hash_value}")
        blocks_of_texts = self.preprocessor.process([{"content": document_content}])

        for block in blocks_of_texts:
            start_index_in_doc = block["meta"]["_split_offset_start"]
            end_index_in_doc = block["meta"]["_split_offset_end"]
            if generated_uuid_for_block := self.ch_client_db.insert_document_block_metadata(
                file_hash=full_file_sha256hash_value,
                file_path=file_path,
                start_idx=start_index_in_doc,
                end_idx=end_index_in_doc,
            ):
                text_chunk = block["content"]
                self.hs_manager_db.add_document_with_embedding(
                    content=text_chunk,
                    doc_id=generated_uuid_for_block,
                    meta={"file_path": file_path}
                )

