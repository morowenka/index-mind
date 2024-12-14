from abc import ABC, abstractmethod
from typing import List, Any

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query_embedding: List[float], *args, **kwargs) -> List[Any]:
        pass
