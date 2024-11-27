# indexmind/backend/tests/test_document_retriever.py

import pytest
from unittest.mock import MagicMock, patch
from src.retrievers.document_retriever import DocumentRetriever
from haystack import Document

@pytest.fixture
def mock_document_store():
    with patch('src.retrievers.document_retriever.get_document_store') as mock_ds:
        yield mock_ds.return_value

@pytest.fixture
def mock_text_embedder():
    with patch('src.retrievers.document_retriever.get_text_embedder') as mock_te:
        yield mock_te.return_value

def test_document_retriever_initialization(mock_document_store, mock_text_embedder):
    retriever = DocumentRetriever()
    assert retriever.document_store == mock_document_store
    assert retriever.text_embedder == mock_text_embedder

def test_retrieve_success(mock_document_store, mock_text_embedder):
    retriever = DocumentRetriever()
    mock_docs = [
        Document(content="Test document 1", id="1", score=0.9, meta={"file_path": "/path/doc1.txt"}),
        Document(content="Test document 2", id="2", score=0.8, meta={"file_path": "/path/doc2.txt"})
    ]
    mock_document_store.get_all_documents.return_value = mock_docs
    mock_text_embedder.embed.return_value = [0.1, 0.2]

    results = retriever.retrieve(query="test query", top_k=2, filters={"category": ["example"]})

    assert len(results) == 2
    assert results[0].content == "Test document 1"
    assert results[1].score == 0.8
