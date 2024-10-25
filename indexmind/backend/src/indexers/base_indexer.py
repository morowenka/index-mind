from abc import ABC, abstractmethod
from typing import List

class BaseIndexer(ABC):
    @abstractmethod
    def add_indexes(self, file_paths: List[str]):
        pass
    
    @abstractmethod
    def update_indexes(self):
        pass
