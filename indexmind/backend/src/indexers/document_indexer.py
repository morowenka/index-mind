# indexmind/backend/src/indexers/document_indexer.py
# TODO: сделать деление на блоки поумнее
# TODO: изменения проверять только у тех, которые не добавлялись только что
from src.indexers.base_indexer import BaseIndexer
from haystack.document_stores.types import DuplicatePolicy
from src.utils.logger import logger
from config import settings
from haystack import Document
import os
import re
import uuid
import time
from typing import List, Dict, Optional
from src.retrievers.document_retriever import document_store, retriever, document_embedder
from src.utils.helpers import hash_content

class DocumentIndexer(BaseIndexer):
    def __init__(self):
        self.document_store = document_store
        self.retriever = retriever
        self.document_embedder = document_embedder

    def add_indexes(self, file_paths: List[str]):
        """
        Adds multiple files to the indexing queue by marking their documents as 'pending'.
        """
        logger.debug(f"Adding {len(file_paths)} files to indexing queue.")
        documents_to_add = []
        
        for file_path in file_paths:
            try:
                logger.debug(f"Processing {file_path}...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                metadata = self._get_file_metadata(file_path, content)
                blocks = self._split_content(
                    content,
                    settings.DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH,
                    settings.DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP
                )
                pending_documents = self._create_pending_documents_without_embeddings(
                    blocks,
                    file_path,
                    metadata
                )
                # for doc in pending_documents:
                #     doc.embedding = [0] * settings.DOCUMENT_STORE_EMBEDDINGS_DIM
                documents_to_add.extend(pending_documents)
                logger.debug(f"Prepared {len(pending_documents)} documents from file {file_path}.")
            except Exception as e:
                logger.error(f"Failed to add file {file_path} to indexing queue: {e}")
        
        if documents_to_add:
            print(documents_to_add)
            self.document_store.write_documents(documents_to_add, policy=DuplicatePolicy.OVERWRITE)
            logger.debug(f"Added {len(documents_to_add)} documents to the document store with status 'pending'.")

    def update_indexes(self):
        """
        Updates indexes by processing pending documents and re-indexing existing documents if their hashes have changed.
        """
        logger.debug("Starting indexing update process.")
        
        # Part 1: Process Pending Documents
        self._process_pending_documents()
        
        # Part 2: Re-index Existing Documents Based on Hash Comparison
        self._reindex_changed_files()

    def _process_pending_documents(self):
        """
        Processes all documents marked as 'pending' by updating their embeddings and marking them as 'indexed'.
        """
        pending_documents = self.document_store.filter_documents(filters={
                "operator": "AND",
                "conditions": [
                    {"field": "meta.status", "operator": "==", "value": "pending"},
                    {"field": "meta.content_type", "operator": "==", "value": "text"},
                    {"field": "meta.source_type", "operator": "==", "value": "document"}
                ]
            }
        )
        logger.debug(f"Found {len(pending_documents)} pending documents to index.")

        if not pending_documents:
            logger.debug("No pending documents to process.")
            return

        documents_with_embeddings = self.document_embedder.run(pending_documents).get("documents")
        for doc in documents_with_embeddings:
            doc.meta['status'] = 'ready'

        self.document_store.write_documents(documents_with_embeddings, policy=DuplicatePolicy.OVERWRITE)
        logger.debug(f"Updated embeddings for {len(documents_with_embeddings)} pending documents.")

    def _reindex_changed_files(self):
        """
        Re-indexes documents from files whose content has changed based on hash comparison.
        """
        all_documents = self.document_store.filter_documents(filters={
                "operator": "AND",
                "conditions": [
                    {"field": "meta.content_type", "operator": "==", "value": "text"},
                    {"field": "meta.source_type", "operator": "==", "value": "document"}
                ]
            }
        )
        unique_file_paths = list({doc.meta.get("file_path") for doc in all_documents if doc.meta.get("file_path")})
        
        logger.debug(f"Checking {len(unique_file_paths)} unique document files for changes.")
        for file_path in unique_file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                current_hash = hash_content(current_content)
                if self._has_file_changed(file_path, current_hash):
                    logger.debug(f"Changes detected in file {file_path}. Re-indexing...")
                    metadata = self._get_file_metadata(file_path, current_content)
                    self._reindex_file(file_path, current_content, metadata)
                else:
                    logger.debug(f"No changes detected in file {file_path}. Skipping re-indexing.")
            except Exception as e:
                logger.error(f"Error during re-indexing of file {file_path}: {e}")

    def _reindex_file(self, file_path: str, content: str, metadata: dict):
        """
        Re-indexes a single file by updating existing documents or adding new ones as necessary.
        """
        blocks = self._split_content(
            content,
            settings.DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH,
            settings.DOC_INDEXER_PREPROCESSOR_SPLIT_OVERLAP
        )
        new_documents_without_embeddings = self._create_pending_documents_without_embeddings(
            blocks,
            file_path,
            metadata
        )
        new_documents: List[Document] = self.document_embedder.run(new_documents_without_embeddings).get("documents")
        
        existing_docs = self.document_store.filter_documents(
            filters={
                "field": "meta.file_path",
                "operator": "==",
                "value": file_path
            }
        )
        num_existing = len(existing_docs)
        num_new = len(new_documents)
        
        documents_to_update = []
        # Update existing documents
        for i, new_doc in enumerate(new_documents):
            if i < num_existing:
                existing_doc = existing_docs[i]
                updated_doc = Document(
                    content=new_doc.content,
                    id=existing_doc.id, # save only existing ID
                    meta=new_doc.meta,
                    embedding=new_doc.embedding
                )
                documents_to_update.append(updated_doc)
            else:
                documents_to_update.append(new_doc)
        
        # Delete excess documents if any
        if num_existing > num_new:
            excess_docs = existing_docs[num_new:]
            excess_ids = [doc.id for doc in excess_docs]
            self.document_store.delete_documents(document_ids=excess_ids)
            logger.debug(f"Deleted {len(excess_ids)} excess documents for file {file_path}.")

        # Bulk write updated and new documents
        if documents_to_update:
            self.document_store.write_documents(documents_to_update, policy=DuplicatePolicy.OVERWRITE)
            logger.debug(f"Updated/Added {len(documents_to_update)} documents for file {file_path}.")

    def _get_file_metadata(self, file_path: str, content: str) -> Dict[str, str]:
        """
        Retrieves metadata for a given file.
        """
        creation_time = os.path.getctime(file_path)
        modification_time = os.path.getmtime(file_path)
        return {
            "creation_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time)),
            "modification_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modification_time)),
            "file_hash": hash_content(content)
        }

    def _has_file_changed(self, file_path: str, current_hash: str) -> bool:
        """
        Determines whether a file has changed by comparing its current hash with the stored hash.
        """
        existing_docs = self.document_store.filter_documents(
            filters={
                "field": "meta.file_path",
                "operator": "==",
                "value": file_path
            }
        )
        if not existing_docs:
            logger.debug(f"No existing documents found for file {file_path}. It will be indexed.")
            return True  # File is new and needs indexing

        existing_hash = existing_docs[0].meta.get("file_hash")
        if existing_hash != current_hash:
            logger.debug(f"Hash mismatch for file {file_path}: existing hash {existing_hash}, current hash {current_hash}.")
            return True
        return False

    def _split_content(self, content: str, max_words: int, overlap_words: int) -> List[Dict]:
        """
        Splits the content into blocks with the specified maximum number of words and word-based overlap.
        """
        words = content.split()
        blocks = []
        total_words = len(words)
        current_pos = 0

        while current_pos < total_words:
            # Определяем диапазон слов для текущего блока
            end_pos = current_pos + max_words
            block_words = words[current_pos:end_pos]
            block_text = ' '.join(block_words)

            # Вычисляем start_idx и end_idx
            # Находим позицию первого слова
            first_word = block_words[0]
            try:
                start_idx = content.index(first_word, current_pos)
            except ValueError:
                start_idx = 0  # На случай, если слово не найдено

            # Находим позицию последнего слова
            last_word = block_words[-1]
            try:
                end_idx = content.index(last_word, start_idx) + len(last_word)
            except ValueError:
                end_idx = len(content)

            blocks.append({
                'content': block_text,
                'start_idx': start_idx,
                'end_idx': end_idx
            })

            # Обновляем позицию для следующего блока с учетом перекрытия
            current_pos += max_words - overlap_words

        return blocks

    def _create_pending_documents_without_embeddings(
        self,
        blocks: List[Dict],
        file_path: str,
        metadata: Dict[str, str]
    ) -> List[Document]:
        """
        Creates Document objects from blocks of text with the appropriate metadata.
        """
        documents = []
        for block in blocks:
            text_chunk = "passage: " + block['content']
            doc_meta = {
                "file_path": file_path,
                "file_hash": metadata["file_hash"],
                "start_idx": block['start_idx'],
                "end_idx": block['end_idx'],
                "creation_time": metadata["creation_time"],
                "modification_time": metadata["modification_time"],
                "content_type": "text",
                "source_type": "document",
                "status": "pending"  # Initially mark as pending
            }
            new_doc = Document(
                content=text_chunk,
                id=str(uuid.uuid4()),
                meta=doc_meta
            )
            documents.append(new_doc)
        return documents
