
from typing import List

from service.api.models.base_model import BaseModel as _BaseModel
from service.api.models.test_model import TestModel


class ModelsBase:
    def __init__(self, models: List[_BaseModel]):
        self.models = {m.model_name: m for m in models}

    def get_model(self, model_name: str) -> _BaseModel:
        return self.models.get(model_name)


AVAILABLE_MODELS = [
    TestModel
]

models_base = ModelsBase(AVAILABLE_MODELS)
