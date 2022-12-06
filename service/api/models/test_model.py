
from typing import List as _List

from service.api.models.base_model import BaseModel as _BaseModel


class TestModel(_BaseModel):
    model_name = 'test_model'

    def __init__(self):
        super().__init__(self.model_name)

    def predict(self, user_id: int, k:int) -> _List[int]:
        return list(range(k))
