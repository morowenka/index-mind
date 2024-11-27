# indexmind/backend/src/indexers/document_indexer.py

import os
import uuid
import time
from typing import List, Dict
from haystack import Document
from haystack.document_stores.types import DuplicatePolicy
from src.utils.logger import logger
from config import settings
from src.stores.document_store import get_document_store
from src.embedders.document_embedder import get_document_embedder
from src.utils.helpers import hash_content

class DocumentIndexer:
    def __init__(self):
        self.document_store = get_document_store()
        self.document_embedder = get_document_embedder()

    def add_indexes(self, file_paths: List[str]):
        logger.info(f"Добавление {len(file_paths)} файлов в очередь на индексацию.")
        documents_to_add = []

        for file_path in file_paths:
            try:
                if self.document_store.filter_documents(filters={
                    "field": "meta.file_path",
                    "operator": "==",
                    "value": file_path
                }):
                    logger.info(f"Файл {file_path} уже существует в хранилище документов. Пропускаем.")
                    continue

                logger.info(f"Обработка файла {file_path}.")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                metadata = self._get_file_metadata(file_path, content)
                blocks = self._split_content(content)
                pending_documents = self._create_documents(blocks, file_path, metadata)
                documents_to_add.extend(pending_documents)
                logger.info(f"Подготовлено {len(pending_documents)} документов из файла {file_path}.")
            except Exception as e:
                logger.error(f"Ошибка при добавлении файла {file_path}: {e}")

        if documents_to_add:
            self.document_store.write_documents(documents_to_add, policy=DuplicatePolicy.OVERWRITE)
            logger.info(f"Добавлено {len(documents_to_add)} документов в хранилище.")
            
    def update_indexes(self):
        logger.info("Проверяем обновления существующих проиндексированных документов...")
        self.reindex_changed_files()
        logger.info("Обновление завершено, начато создание индексов для новых файлов.")
        pending_documents = self.document_store.filter_documents(filters={
                "operator": "AND",
                "conditions": [
                    {"field": "meta.status", "operator": "==", "value": "pending"}                ]
            }
        )
        logger.info(f"Найдено {len(pending_documents)} текстовых документов со статусом 'pending'.")

        if not pending_documents:
            logger.info("Нет документов для обновления.")
            return

        processed_documents = self.document_embedder.run(pending_documents)['documents']
        for doc in processed_documents:
            doc.meta['status'] = 'ready'

        self.document_store.write_documents(processed_documents, policy=DuplicatePolicy.OVERWRITE)
        logger.info("Обновление индексов завершено.")
        
        
    def reindex_changed_files(self):
        """
        Re-indexes documents from files whose content has changed based on hash comparison.
        """
        logger.info("Начало проверки изменений файлов для переиндексации.")
        all_documents = self.document_store.filter_documents(filters=None)

        unique_file_paths = list({doc.meta.get("file_path") for doc in all_documents if doc.meta.get("file_path")})
        logger.info(f"Проверка {len(unique_file_paths)} уникальных файлов на изменения.")

        for file_path in unique_file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                current_hash = hash_content(current_content)

                # Получаем старый хэш файла из метаданных
                existing_doc = next(
                    (doc for doc in all_documents if doc.meta.get("file_path") == file_path), None
                )
                if not existing_doc:
                    logger.warning(f"Файл {file_path} не найден в текущих документах. Пропускаем.")
                    continue

                old_hash = existing_doc.meta.get("file_hash")
                if current_hash != old_hash:
                    logger.info(f"Изменения обнаружены в файле {file_path}. Переиндексация...")
                    metadata = self._get_file_metadata(file_path, current_content)
                    self._reindex_file(file_path, current_content, metadata)
                else:
                    logger.info(f"Изменений в файле {file_path} не обнаружено.")
            except Exception as e:
                logger.error(f"Ошибка при обработке файла {file_path}: {e}")

    def _reindex_file(self, file_path: str, content: str, metadata: dict):
        """
        Re-indexes a single file by updating existing documents or adding new ones as necessary.
        """
        logger.info(f"Начало переиндексации файла {file_path}.")
        blocks = self._split_content(content)
        new_documents = self._create_documents(blocks, file_path, metadata)

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

        for i, new_doc in enumerate(new_documents):
            if i < num_existing:
                existing_doc = existing_docs[i]
                updated_doc = Document(
                    content=new_doc.content,
                    id=existing_doc.id,  # сохраняем существующий ID
                    meta=new_doc.meta,
                    embedding=new_doc.embedding
                )
                documents_to_update.append(updated_doc)
            else:
                documents_to_update.append(new_doc)

        if num_existing > num_new:
            excess_docs = existing_docs[num_new:]
            excess_ids = [doc.id for doc in excess_docs]
            self.document_store.delete_documents(document_ids=excess_ids)
            logger.info(f"Удалено {len(excess_ids)} лишних документов для файла {file_path}.")

        if documents_to_update:
            self.document_store.write_documents(documents_to_update, policy=DuplicatePolicy.OVERWRITE)
            logger.info(f"Обновлено/добавлено {len(documents_to_update)} документов для файла {file_path}.")
    

    def _get_file_metadata(self, file_path: str, content: str) -> Dict[str, str]:
        creation_time = os.path.getctime(file_path)
        modification_time = os.path.getmtime(file_path)
        return {
            "creation_time": time.mktime(time.localtime(creation_time)),
            "modification_time": time.mktime(time.localtime(modification_time)),
            "file_hash": hash_content(content)
        }

    def _split_content(self, content: str) -> List[str]:
        max_length = settings.DOC_INDEXER_PREPROCESSOR_MAX_WORDS_SPLIT_LENGTH
        words = content.split()
        return [' '.join(words[i:i + max_length]) for i in range(0, len(words), max_length)]

    def _create_documents(self, blocks: List[str], file_path: str, metadata: Dict[str, str]) -> List[Document]:
        documents = []
        for block in blocks:
            doc_meta = {
                "file_path": file_path,
                **metadata,
                "status": "pending"
            }
            new_doc = Document(
                content=block,
                meta=doc_meta,
                id=str(uuid.uuid4())
            )
            documents.append(new_doc)
        return documents
    
    def delete_all_documents(self):
        try:
            total_documents = self.document_store.count_documents()
            logger.info(f"Удаление всех {total_documents} документов из хранилища.")
            document_ids = [doc.id for doc in self.document_store.filter_documents(filters=None)]
            self.document_store.delete_documents(document_ids)
            logger.info("Все документы успешно удалены.")
            return {"message": "Все документы успешно удалены", "total_deleted": total_documents}
        except Exception as e:
            logger.error(f"Ошибка при удалении документов: {e}")
            raise RuntimeError(f"Ошибка при удалении документов: {str(e)}") from e
