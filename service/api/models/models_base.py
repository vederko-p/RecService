
from typing import List as _List

from service.api.models.base_model import BaseModel
from service.api.models.test_model import test_model
from service.api.models.knn_model import knn_model


class ModelsBase:
    def __init__(self, models: _List[BaseModel]):
        self.models = {m.model_name: m for m in models}

    def check_model(self, model_name: str) -> bool:
        return self.models.get(model_name) is not None


    def init_model(self, model_name: str) -> BaseModel:
        return self.models.get(model_name)


AVAILABLE_MODELS = [
    test_model,
    knn_model
]

models_base = ModelsBase(AVAILABLE_MODELS)
