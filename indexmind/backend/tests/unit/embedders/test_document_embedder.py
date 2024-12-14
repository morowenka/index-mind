# tests/unit/embedders/test_document_embedder.py

import pytest
from unittest.mock import patch, MagicMock
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack import Document
from src.embedders.document_embedder import get_document_embedder
from config import settings

@pytest.fixture
def mock_sentence_transformers():
    """Фикстура для мока SentenceTransformersDocumentEmbedder"""
    with patch('src.embedders.document_embedder.SentenceTransformersDocumentEmbedder', autospec=True) as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def sample_documents():
    """Фикстура с тестовыми документами"""
    return [
        Document(
            content="Test document 1",
            meta={"file_path": "/test/doc1.txt"}
        ),
        Document(
            content="Test document 2",
            meta={"file_path": "/test/doc2.txt"}
        )
    ]

def test_document_embedder_singleton():
    """Проверка реализации паттерна Singleton"""
    embedder1 = get_document_embedder()
    embedder2 = get_document_embedder()
    assert embedder1 is embedder2

def test_document_embedder_initialization(mock_sentence_transformers):
    """Проверка правильности инициализации embedder'а"""
    # Reset the singleton instance
    with patch('src.embedders.document_embedder._document_embedder', None):
        embedder = get_document_embedder()
        
        mock_sentence_transformers.assert_called_once_with(
            model=settings.DOC_EMBEDDER_MODEL,
            precision=settings.DOC_EMBEDDER_PRECISION,
            batch_size=settings.DOC_EMBEDDER_BATCH_SIZE,
            progress_bar=settings.DOC_EMBEDDER_PROGRESS_BAR
        )
        
        mock_sentence_transformers.return_value.warm_up.assert_called_once()

def test_document_embedder_with_documents(mock_sentence_transformers, sample_documents):
    """Проверка работы embedder'а с документами"""
    embedder = get_document_embedder()
    
    # Создаем мок эмбеддингов правильной размерности
    mock_embeddings = [[0.1] * settings.DOCUMENT_STORE_EMBEDDINGS_DIM for _ in sample_documents]
    mock_sentence_transformers.return_value.run.return_value = {
        'documents': [
            Document(content=doc.content, embedding=emb, meta=doc.meta)
            for doc, emb in zip(sample_documents, mock_embeddings)
        ]
    }
    
    # Запускаем embedder
    result = embedder.run(documents=sample_documents)
    
    # Проверяем результаты
    assert 'documents' in result
    assert len(result['documents']) == len(sample_documents)
    for doc, emb in zip(result['documents'], mock_embeddings):
        assert doc.embedding is not None
        assert len(doc.embedding) == len(emb)

def test_document_embedder_empty_input(mock_sentence_transformers):
    """Проверка работы embedder'а с пустым входом"""
    embedder = get_document_embedder()
    
    # Настраиваем мок для пустого входа
    mock_sentence_transformers.run.return_value = {'documents': []}
    
    # Запускаем embedder с пустым списком
    result = embedder.run(documents=[])
    
    # Проверяем результаты
    assert 'documents' in result
    assert len(result['documents']) == 0

def test_document_embedder_error_handling(mock_sentence_transformers):
    """Проверка обработки ошибок"""
    # Reset the singleton instance
    with patch('src.embedders.document_embedder._document_embedder', None):
        embedder = get_document_embedder()
        # Configure mock to raise exception during run
        mock_sentence_transformers.return_value.run.side_effect = RuntimeError("Test error")
        
        with pytest.raises(RuntimeError, match="Test error"):
            embedder.run(documents=[Document(content="test")])

@pytest.mark.parametrize("doc_content,expected_shape", [
    ("Short text", settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
    ("Long text " * 100, settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
    ("", settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
    ("Special chars !@#$%", settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
])
def test_document_embedder_different_inputs(mock_sentence_transformers, doc_content, expected_shape):
    """Проверка работы embedder'а с разными типами входных данных"""
    embedder = get_document_embedder()
    
    # Создаем мок эмбеддинга нужной размерности
    mock_embedding = [0.1] * expected_shape
    mock_sentence_transformers.run.return_value = {
        'documents': [Document(content=doc_content, embedding=mock_embedding)]
    }
    
    # Запускаем embedder
    result = embedder.run(documents=[Document(content=doc_content)])
    
    # Проверяем результаты
    assert len(result['documents'][0].embedding) == expected_shape

def test_document_embedder_batch_processing(mock_sentence_transformers):
    """Проверка пакетной обработки документов"""
    embedder = get_document_embedder()
    
    # Создаем большой набор документов
    large_doc_set = [Document(content=f"Doc {i}") for i in range(100)]
    mock_embeddings = [[0.1, 0.2, 0.3] for _ in range(100)]
    
    # Настраиваем мок для пакетной обработки
    mock_sentence_transformers.run.return_value = {
        'documents': [
            Document(content=doc.content, embedding=emb)
            for doc, emb in zip(large_doc_set, mock_embeddings)
        ]
    }
    
    # Запускаем embedder
    result = embedder.run(documents=large_doc_set)
    
    # Проверяем результаты
    assert len(result['documents']) == len(large_doc_set)
    # Проверяем, что все документы получили эмбеддинги
    assert all(doc.embedding is not None for doc in result['documents'])

def test_document_embedder_model_loading():
    """Проверка загрузки модели"""
    with patch('src.embedders.document_embedder._document_embedder', None):  # Reset singleton
        with patch('src.embedders.document_embedder.SentenceTransformersDocumentEmbedder', autospec=True) as mock_embedder:
            embedder1 = get_document_embedder()
            assert mock_embedder.call_count == 1
            
            embedder2 = get_document_embedder()
            assert mock_embedder.call_count == 1  # Не должно быть нового вызова
