# tests/unit/embedders/test_text_embedder.py

import pytest
from unittest.mock import patch, MagicMock
from haystack.components.embedders import SentenceTransformersTextEmbedder
from src.embedders.text_embedder import get_text_embedder
from config import settings


def test_text_embedder_singleton():
    """Проверка реализации паттерна Singleton"""
    embedder1 = get_text_embedder()
    embedder2 = get_text_embedder()
    assert embedder1 is embedder2

def test_text_embedder_initialization(mock_sentence_transformers):
    """Проверка правильности инициализации embedder'а"""
    with patch('src.embedders.text_embedder._text_embedder', None):
        embedder = get_text_embedder()
        
        mock_sentence_transformers.assert_called_once_with(
            model=settings.DOC_EMBEDDER_MODEL,
            precision=settings.DOC_EMBEDDER_PRECISION,
            batch_size=settings.DOC_EMBEDDER_BATCH_SIZE,
            progress_bar=settings.DOC_EMBEDDER_PROGRESS_BAR
        )
        
        mock_sentence_transformers.return_value.warm_up.assert_called_once()

def test_text_embedder_with_texts(mock_sentence_transformers, sample_texts):
    """Проверка работы embedder'а с текстом"""
    embedder = get_text_embedder()
    
    mock_embedding = [0.1] * settings.DOCUMENT_STORE_EMBEDDINGS_DIM
    mock_sentence_transformers.return_value.run.return_value = {'embedding': mock_embedding}
    
    for text in sample_texts:
        result = embedder.run(text=text)
        assert 'embedding' in result
        assert len(result['embedding']) == settings.DOCUMENT_STORE_EMBEDDINGS_DIM

def test_text_embedder_empty_input(mock_sentence_transformers):
    """Проверка работы embedder'а с пустым входом"""
    embedder = get_text_embedder()
    mock_embedding = [0.1] * settings.DOCUMENT_STORE_EMBEDDINGS_DIM
    mock_sentence_transformers.return_value.run.return_value = {'embedding': mock_embedding}
    
    result = embedder.run(text="")
    assert 'embedding' in result
    assert len(result['embedding']) == settings.DOCUMENT_STORE_EMBEDDINGS_DIM

def test_text_embedder_error_handling(mock_sentence_transformers):
    """Проверка обработки ошибок"""
    with patch('src.embedders.text_embedder._text_embedder', None):
        embedder = get_text_embedder()
        mock_sentence_transformers.return_value.run.side_effect = RuntimeError("Test error")
        
        with pytest.raises(RuntimeError, match="Test error"):
            embedder.run(text="test")

@pytest.mark.parametrize("text_content,expected_shape", [
    ("Short text", settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
    ("Long text " * 100, settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
    ("", settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
    ("Special chars !@#$%", settings.DOCUMENT_STORE_EMBEDDINGS_DIM),
])
def test_text_embedder_different_inputs(mock_sentence_transformers, text_content, expected_shape):
    """Проверка работы embedder'а с разными типами входных данных"""
    embedder = get_text_embedder()
    
    mock_embedding = [0.1] * expected_shape
    mock_sentence_transformers.return_value.run.return_value = {'embedding': mock_embedding}
    
    result = embedder.run(text=text_content)
    assert len(result['embedding']) == expected_shape

def test_text_embedder_batch_processing(mock_sentence_transformers):
    """Проверка последовательной обработки текстов"""
    embedder = get_text_embedder()
    
    texts = [f"Text {i}" for i in range(3)]
    mock_embedding = [0.1] * settings.DOCUMENT_STORE_EMBEDDINGS_DIM
    mock_sentence_transformers.return_value.run.return_value = {'embedding': mock_embedding}
    
    results = []
    for text in texts:
        result = embedder.run(text=text)
        results.append(result['embedding'])
    
    assert len(results) == len(texts)
    assert all(len(emb) == settings.DOCUMENT_STORE_EMBEDDINGS_DIM for emb in results)

def test_text_embedder_model_loading():
    """Проверка загрузки модели"""
    with patch('src.embedders.text_embedder._text_embedder', None):
        with patch('src.embedders.text_embedder.SentenceTransformersTextEmbedder', autospec=True) as mock_embedder:
            embedder1 = get_text_embedder()
            assert mock_embedder.call_count == 1
            
            embedder2 = get_text_embedder()
            assert mock_embedder.call_count == 1
