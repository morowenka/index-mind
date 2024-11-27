# tests/test_index_manager.py

import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from src.managers.index_manager import IndexManager
from src.indexers.document_indexer import DocumentIndexer
from src.indexers.image_indexer import ImageIndexer

@pytest.fixture
def mock_document_indexer():
    with patch('src.index_manager.DocumentIndexer') as MockIndexer:
        yield MockIndexer.return_value

@pytest.fixture
def mock_image_indexer():
    with patch('src.index_manager.ImageIndexer') as MockIndexer:
        yield MockIndexer.return_value

@pytest.fixture
def mock_manager():
    return MagicMock()

@pytest.mark.asyncio
async def test_add_indexes_async(mock_document_indexer, mock_image_indexer, mock_manager):
    index_manager = IndexManager()
    file_paths = ['/path/to/doc1.txt', '/path/to/doc2.txt']

    # Mock methods
    index_manager.count_total_files = MagicMock(return_value=2)
    index_manager._send_json_safely = AsyncMock()
    index_manager._add_single_file = MagicMock(return_value=True)

    # Run the async method
    await index_manager.add_indexes_async(file_paths, mock_manager)

    # Assertions
    index_manager._add_single_file.assert_any_call('/path/to/doc1.txt')
    index_manager._add_single_file.assert_any_call('/path/to/doc2.txt')
    index_manager._send_json_safely.assert_any_call(mock_manager, {"total_files": 2})
