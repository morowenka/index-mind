from abc import ABC, abstractmethod


class BaseIndexer(ABC):
    @abstractmethod
    def index(self, file_path: str):
        pass
