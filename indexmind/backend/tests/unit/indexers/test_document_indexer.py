import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.indexers.document_indexer import DocumentIndexer
from src.indexers.base_indexer import BaseIndexer
from haystack import Document
from config import settings
import os.path

@pytest.fixture
def mock_document_store():
    """Фикстура для мока DocumentStore"""
    with patch('src.indexers.document_indexer.get_document_store') as mock:
        mock_store = MagicMock()
        mock.return_value = mock_store
        # Configure default return values
        mock_store.filter_documents.return_value = []
        mock_store.write_documents.return_value = None
        yield mock_store

@pytest.fixture
def mock_document_embedder():
    with patch('src.indexers.document_indexer.get_document_embedder') as mock:
        mock_embedder = MagicMock()
        mock.return_value = mock_embedder
        yield mock_embedder

@pytest.fixture
def document_indexer(mock_document_store, mock_document_embedder):
    return DocumentIndexer()

@pytest.fixture
def mock_file_operations():
    """Фикстура для мока операций с файлами"""
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.getmtime') as mock_mtime, \
         patch('os.path.getctime') as mock_ctime:
        mock_exists.return_value = True
        mock_mtime.return_value = 1234567890
        mock_ctime.return_value = 1234567890
        yield mock_exists, mock_mtime, mock_ctime

def test_document_indexer_implements_base_indexer():
    """Проверка, что DocumentIndexer реализует BaseIndexer"""
    indexer = DocumentIndexer()
    assert isinstance(indexer, BaseIndexer)

def test_add_indexes_new_file(document_indexer, mock_document_store, mock_file_operations):
    """Проверка добавления нового файла"""
    file_content = "Test content"
    file_path = "/test/file.txt"
    mock_document_store.filter_documents.return_value = []  # Файл еще не существует
    
    with patch('builtins.open', mock_open(read_data=file_content)) as mock_file:
        document_indexer.add_indexes([file_path])
    
    # Verify write_documents was called
    mock_document_store.write_documents.assert_called_once()
    written_docs = mock_document_store.write_documents.call_args[0][0]
    assert len(written_docs) > 0
    assert all(isinstance(doc, Document) for doc in written_docs)
    assert all(doc.meta['file_path'] == file_path for doc in written_docs)

def test_add_indexes_existing_file(document_indexer, mock_document_store):
    """Проверка попытки добавления существующего файла"""
    file_path = "/test/file.txt"
    mock_document_store.filter_documents.return_value = [Document(content="Existing")]
    
    document_indexer.add_indexes([file_path])
    
    # Проверяем, что документы не были записаны
    mock_document_store.write_documents.assert_not_called()

def test_update_indexes(document_indexer, mock_document_store, mock_document_embedder):
    """Проверка обновления индексов"""
    # Подготовка
    pending_docs = [Document(content="test", meta={"status": "pending"})]
    mock_document_store.filter_documents.return_value = pending_docs
    mock_document_embedder.run.return_value = {
        'documents': [Document(content="test", meta={"status": "ready"}, embedding=[0.1] * settings.DOCUMENT_STORE_EMBEDDINGS_DIM)]
    }
    
    # Выполнение
    document_indexer.update_indexes()
    
    # Проверка
    mock_document_embedder.run.assert_called_once_with(pending_docs)
    mock_document_store.write_documents.assert_called_once()
    updated_docs = mock_document_store.write_documents.call_args[0][0]
    assert all(doc.meta['status'] == 'ready' for doc in updated_docs)

def test_reindex_changed_files(document_indexer, mock_document_store, mock_file_operations):
    """Проверка переиндексации измененных файлов"""
    # Подготовка
    old_content = "Old content"
    new_content = "New content"
    file_path = "/test/file.txt"
    existing_doc = Document(
        content=old_content,
        meta={
            "file_path": file_path,
            "file_hash": "old_hash",
            "status": "ready"
        }
    )
    mock_document_store.filter_documents.return_value = [existing_doc]
    
    # Мокаем открытие файла с новым содержимым
    with patch('builtins.open', mock_open(read_data=new_content)):
        document_indexer.reindex_changed_files()
    
    # Проверка
    mock_document_store.write_documents.assert_called_once()
    reindexed_docs = mock_document_store.write_documents.call_args[0][0]
    assert len(reindexed_docs) > 0
    assert all(doc.meta['file_path'] == file_path for doc in reindexed_docs)

def test_delete_all_documents(document_indexer, mock_document_store):
    """Проверка удаления всех документов"""
    # Подготовка
    mock_document_store.count_documents.return_value = 2
    mock_document_store.filter_documents.return_value = [
        Document(id="1", content="doc1"),
        Document(id="2", content="doc2")
    ]
    
    # Выполнение
    result = document_indexer.delete_all_documents()
    
    # Проверка
    mock_document_store.delete_documents.assert_called_once()
    assert result["total_deleted"] == 2
    assert "message" in result

def test_error_handling(mock_document_store):
    """Проверка обработки ошибок"""
    indexer = DocumentIndexer()
    mock_document_store.filter_documents.side_effect = RuntimeError("Test error")
    
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True  # Make file existence check pass
        with pytest.raises(RuntimeError, match="Test error"):
            indexer.add_indexes(["/test/file.txt"])
