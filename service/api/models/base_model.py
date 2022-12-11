from abc import ABC, abstractmethod
from typing import List


class BaseModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def predict(self, user_id: int, k: int) -> List[int]:
        pass
