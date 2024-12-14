import pytest
from typing import Dict, Any
import sys
import os
from unittest.mock import patch, MagicMock
from config import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Базовая фикстура с конфигурацией для тестов"""
    return {
        "test_data_dir": "tests/fixtures/data",
        "mock_responses_dir": "tests/fixtures/mock_responses"
    }

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """Установка переменных окружения для тестов"""
    monkeypatch.setenv("TESTING", "true")

@pytest.fixture
def mock_document_embedder():
    """Фикстура для мока DocumentEmbedder"""
    with patch('src.embedders.document_embedder.get_document_embedder') as mock:
        mock_embedder = MagicMock()
        mock.return_value = mock_embedder
        yield mock_embedder

@pytest.fixture
def mock_text_embedder():
    """Фикстура для мока TextEmbedder"""
    with patch('src.embedders.text_embedder.get_text_embedder') as mock:
        mock_embedder = MagicMock()
        mock.return_value = mock_embedder
        yield mock_embedder

@pytest.fixture
def sample_embeddings():
    """Фикстура с примерами эмбеддингов"""
    return [
        [0.1, 0.2, 0.3] * (settings.DOCUMENT_STORE_EMBEDDINGS_DIM // 3),
        [0.4, 0.5, 0.6] * (settings.DOCUMENT_STORE_EMBEDDINGS_DIM // 3)
    ]

@pytest.fixture
def mock_sentence_transformers():
    """Фикстура для мока SentenceTransformersTextEmbedder"""
    with patch('src.embedders.text_embedder.SentenceTransformersTextEmbedder', autospec=True) as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def sample_texts():
    """Фикстура с тестовыми текстами"""
    return [
        "Test text 1",
        "Test text 2"
    ]
