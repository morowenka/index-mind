# tests/test_document_retriever.py

import pytest
from unittest.mock import MagicMock, patch
from src.retrievers.document_retriever import DocumentRetriever
from haystack.schema import Document

@pytest.fixture
def mock_document_store():
    with patch('src.retrievers.document_retriever.document_store') as mock_ds:
        yield mock_ds

@pytest.fixture
def mock_retriever():
    with patch('src.retrievers.document_retriever.retriever') as mock_ret:
        yield mock_ret

def test_document_retriever_initialization(mock_document_store, mock_retriever):
    retriever = DocumentRetriever()
    assert retriever.document_store == mock_document_store
    assert retriever.retriever == mock_retriever

def test_retrieve_success(mock_document_store, mock_retriever):
    # Arrange
    retriever = DocumentRetriever()
    mock_docs = [
        Document(content="Test document 1", id="1", score=0.9, meta={"file_path": "/path/doc1.txt"}),
        Document(content="Test document 2", id="2", score=0.8, meta={"file_path": "/path/doc2.txt"})
    ]
    mock_retriever.retrieve.return_value = mock_docs
    results = retriever.retrieve(query="test query", top_k=2, filters={"category": ["example"]})

    # Assert
    mock_retriever.retrieve.assert_called_once_with(query="query: test query", top_k=2, filters={"category": ["example"], "status": ["indexed"]})
    assert len(results) == 2
    assert results[0].content == "Test document 1"
    assert results[1].score == 0.8

def test_retrieve_no_filters(mock_retriever):
    # Arrange
    retriever = DocumentRetriever()
    mock_docs = [
        Document(content="Test document 1", id="1", score=0.9, meta={"file_path": "/path/doc1.txt"})
    ]
    mock_retriever.retrieve.return_value = mock_docs

    # Act
    results = retriever.retrieve(query="another query")

    # Assert
    mock_retriever.retrieve.assert_called_once_with(query="query: another query", top_k=5, filters={"status": ["indexed"]})
    assert len(results) == 1
    assert results[0].content == "Test document 1"

def test_retrieve_handles_exceptions(mock_retriever, caplog):
    # Arrange
    retriever = DocumentRetriever()
    mock_retriever.retrieve.side_effect = Exception("Retrieval error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        retriever.retrieve(query="error query")
    assert "Retrieval error" in str(exc_info.value)
    assert "Retrieving for query: 'error query'" in caplog.text
