from typing import List

from service.api.models.base_model import BaseModel
from service.log import app_logger


class TestModel(BaseModel):
    model_name = "test_model"

    def __init__(self):
        super().__init__(self.model_name)

    def predict(self, user_id: int, k: int) -> List[int]:
        return list(range(k))


app_logger.info("Test Model initialization...")
test_model: TestModel = TestModel()
