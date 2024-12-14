# indexmind/backend/src/managers/index_manager.py

import os
import asyncio
from typing import List
from src.indexers.document_indexer import DocumentIndexer
from src.indexers.image_indexer import ImageIndexer
from src.indexers.pdf_indexer import PDFIndexer
from src.utils.logger import logger
from schemas.file_types import DocumentFile, ImageFile, PDFFile
import traceback
import json

FILE_TYPES = [DocumentFile, ImageFile, PDFFile]

class IndexManager:
    def __init__(self):
        self.indexers = {
            'document': DocumentIndexer(),
            'image': ImageIndexer(),
            'pdf': PDFIndexer()
        }

    def delete_all_documents(self):
        logger.info("Начало удаления всех документов из хранилища.")
        try:
            for indexer_key, indexer in self.indexers.items():
                try:
                    indexer.clear_indexes()
                    logger.info(f"Индексы для {indexer_key} успешно очищены.")
                except Exception as e:
                    logger.error(f"Ошибка при очистке индексов для {indexer_key}: {e}")
            logger.info("Удаление всех документов завершено.")
        except Exception as e:
            logger.error(f"Ошибка при удалении документов: {e}")
            raise Exception(f"Не удалось удалить все документы: {e}") from e

    async def add_indexes_async(self, file_paths: List[str], manager):
        logger.info("Начало асинхронной индексации документов.")
        try:
            total_files = self.count_total_files(file_paths)
            await self._send_json_safely(manager, {"total_files": total_files})
            logger.info(f"Общее количество файлов для индексации: {total_files}")

            processed_files = 0
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.warning(f"Путь {file_path} не существует.")
                    continue

                if os.path.isdir(file_path):
                    for root, dirs, files in os.walk(file_path):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
                            if file.startswith('.'):
                                continue
                            full_path = os.path.join(root, file)
                            if self._add_single_file(full_path):
                                processed_files += 1
                                await self._send_json_safely(manager, {
                                    "processed_file": full_path,
                                    "current_progress": processed_files,
                                    "total_files": total_files
                                })
                                logger.info(f"Файл {full_path} успешно обработан.")
                elif os.path.isfile(file_path):
                    if self._add_single_file(file_path):
                        processed_files += 1
                        await self._send_json_safely(manager, {
                            "processed_file": file_path,
                            "current_progress": processed_files,
                            "total_files": total_files
                        })
                        logger.info(f"Файл {file_path} успешно обработан.")
                else:
                    logger.warning(f"Путь {file_path} не является валидным файлом или директорией.")

            await self._send_json_safely(manager, {"indexing_complete": True})
            logger.info("Асинхронная индексация документов завершена.")
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Ошибка при асинхронной индексации: {e}")
            await self._send_json_safely(manager, {
                "error": str(e),
                "trace": error_trace
            })

    def count_total_files(self, file_paths: List[str]) -> int:
        total_files = 0
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"Путь {file_path} не существует.")
                continue

            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    total_files += len([file for file in files if not file.startswith('.')])
            elif os.path.isfile(file_path):
                total_files += 1
            else:
                logger.warning(f"Путь {file_path} не является валидным файлом или директорией.")

        return total_files

    def _add_single_file(self, file_path: str) -> bool:
        file_extension = os.path.splitext(file_path)[1].lower()
        for file_type_class in FILE_TYPES:
            if file_type_class.matches_extension(file_extension):
                indexer_key = file_type_class.indexer_key
                if indexer := self.indexers.get(indexer_key):
                    try:
                        indexer.add_indexes([file_path])
                        logger.info(f"Файл {file_path} добавлен в очередь на индексацию.")
                        return True
                    except PermissionError as e:
                        logger.error(f"Доступ запрещен для файла {file_path}: {e}")
                    return False

        logger.warning(f"Нет индексатора для типа файла: {file_path}")
        return False

    async def update_indexes_async(self, manager):
        logger.info("Начало асинхронного обновления индексов.")
        try:
            for indexer_key, indexer in self.indexers.items():
                try:
                    indexer.update_indexes()
                    await self._send_json_safely(manager, {
                        "indexer": indexer_key,
                        "status": "completed"
                    })
                    logger.info(f"Индексы для {indexer_key} успешно обновлены.")
                except Exception as e:
                    logger.error(f"Ошибка при обновлении индексов для {indexer_key}: {e}")
                    await self._send_json_safely(manager, {
                        "indexer": indexer_key,
                        "error": str(e)
                    })
            await self._send_json_safely(manager, {"update_indexes_complete": True})
            logger.info("Асинхронное обновление индексов завершено.")
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Ошибка при асинхронном обновлении индексов: {e}")
            await self._send_json_safely(manager, {
                "error": str(e),
                "trace": error_trace
            })

    async def _send_json_safely(self, manager, data: dict):
        try:
            json_data = json.dumps(data)
            await manager.send_message(data)
            logger.info(f"Sent WebSocket message: {json_data}")
        except Exception as e:
            logger.error(f"WebSocket send error: {e} - Data: {data}")
