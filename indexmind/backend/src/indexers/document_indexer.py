# indexmind/backend/src/indexers/document_indexer.py

from src.indexers.base_indexer import BaseIndexer
from src.utils.logger import logger
from config import settings
from haystack.nodes import PreProcessor
from haystack.schema import Document
import hashlib
import os
import re
import uuid
import time
from typing import List, Dict
from src.retrievers.document_retriever import document_store, retriever
from src.utils.helpers import hash_content

class DocumentIndexer(BaseIndexer):
    def __init__(self):
        self.document_store = document_store
        self.retriever = retriever

    def index(self, file_path: str):  # sourcery skip: use-named-expression
        logger.debug(f"Indexing file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return

        full_file_sha256hash_value = hash_content(content)
        existing_docs = self.document_store.get_all_documents(filters={"file_path": [file_path]})

        if existing_docs:
            existing_hash = existing_docs[0].meta.get("file_hash", None)
            if existing_hash == full_file_sha256hash_value:
                logger.debug(f"File {file_path} has not changed. Skipping reindexing.")
                return
            else:
                logger.debug(f"File {file_path} has changed. Updating documents.")

        # Split content into blocks
        sentences = _split_into_sentences(content)
        blocks = _split_into_blocks(sentences, max_words=settings.DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH, content=content)

        creation_time = os.path.getctime(file_path)
        modification_time = os.path.getmtime(file_path)
        creation_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
        modification_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modification_time))

        # Update existing documents or add new ones
        documents_to_update = []
        for i, block in enumerate(blocks):
            start_idx = block['start_idx']
            end_idx = block['end_idx']
            text_chunk = "passage: " + block['content']

            meta = {
                "file_path": file_path,
                "file_hash": full_file_sha256hash_value,
                "start_idx": start_idx,
                "end_idx": end_idx,
                "creation_time": creation_time_str,
                "modification_time": modification_time_str,
                "type": "text"
            }

            if i < len(existing_docs):
                # Update existing document
                existing_doc = existing_docs[i]
                existing_doc.content = text_chunk
                existing_doc.meta = meta
                documents_to_update.append(existing_doc)
            else:
                # Add new document
                new_doc = Document(content=text_chunk, id=str(uuid.uuid4()), meta=meta)
                documents_to_update.append(new_doc)

        if documents_to_update:
            self.document_store.write_documents(documents_to_update)
            logger.debug(f"Updated/Added {len(documents_to_update)} documents to the document store.")
            for doc in documents_to_update:
                logger.debug(f"Document ID: {doc.id}")

            # Update embeddings for the documents
            self.document_store.update_embeddings(
                retriever=self.retriever,
                update_existing_embeddings=True  # Update embeddings for modified documents
            )
            self.document_store.save(
                index_path=settings.DOCUMENT_FAISS_INDEX_PATH,
                config_path=settings.DOCUMENT_FAISS_CONFIG_PATH
            )


# TODO: add overlap
def _split_into_sentences(text: str) -> List:
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    return sentence_endings.split(text)

def _split_into_blocks(sentences: list, max_words: int, content: str) -> List[Dict]:
    blocks = []
    current_block = []
    current_word_count = 0
    current_start_idx = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        if current_word_count + word_count > max_words:
            block_content = ' '.join(current_block)
            block_end_idx = current_start_idx + len(block_content)
            blocks.append({
                'content': block_content,
                'start_idx': current_start_idx,
                'end_idx': block_end_idx
            })
            current_block = []
            current_word_count = 0
            current_start_idx = content.find(sentence, block_end_idx)
        current_block.append(sentence)
        current_word_count += word_count

    if current_block:
        block_content = ' '.join(current_block)
        block_end_idx = current_start_idx + len(block_content)
        blocks.append({
            'content': block_content,
            'start_idx': current_start_idx,
            'end_idx': block_end_idx
        })

    return blocks
