import pytest
from src.indexers.base_indexer import BaseIndexer
from typing import List

def test_cannot_instantiate_abstract_base_indexer():
    """Проверка, что нельзя создать экземпляр абстрактного класса"""
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class BaseIndexer"):
        BaseIndexer()

def test_concrete_indexer_must_implement_abstract_methods():
    """Проверка, что конкретный класс должен реализовать абстрактные методы"""
    class IncompleteIndexer(BaseIndexer):
        pass

    with pytest.raises(TypeError):
        IncompleteIndexer()

def test_minimal_concrete_indexer():
    """Проверка минимальной корректной реализации"""
    class MinimalIndexer(BaseIndexer):
        def add_indexes(self, file_paths: List[str]):
            pass
        
        def update_indexes(self):
            pass

    # Не должно вызывать исключений
    indexer = MinimalIndexer()
    assert isinstance(indexer, BaseIndexer)
