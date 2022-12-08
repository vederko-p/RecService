from typing import List

from service.api.models.base_model import BaseModel
from service.api.models.test_model import TestModel


class ModelsBase:
    def __init__(self, models: List[BaseModel]):
        self.models = {m.model_name: m for m in models}

    def check_model(self, model_name: str) -> bool:
        return self.models.get(model_name) is not None

    def init_model(self, model_name: str) -> BaseModel:
        model_link = self.models.get(model_name)
        model = model_link()
        return model


AVAILABLE_MODELS = [TestModel]

models_base = ModelsBase(AVAILABLE_MODELS)
