from typing import Any, Dict, List, Tuple, Union

import dill
import pandas as pd

from service.api.models.base_model import BaseModel
from service.log import app_logger


class KNNModel(BaseModel):
    model_name = "knn_model"

    def __init__(
        self,
        user_segment_map: Dict[int, int],
        segment_model_map: Dict[int, Any],
        pop_items: List[int],
        warmup_k: int = None,
    ):
        super().__init__(self.model_name)
        self.user_segment_map = user_segment_map
        self.segment_model_map = segment_model_map
        self.pop_items = pop_items
        self.warmup_k = 10 if warmup_k is None else warmup_k

    def predict(self, user_id: int, k: int) -> List[int]:
        user_segment = self.user_segment_map.get(user_id)
        if user_segment is None:
            return self._predict_popular(k)
        else:
            return self._predict_by_model(user_id, user_segment, k)

    def _predict_popular(self, k: int) -> List[int]:
        return list(self.pop_items)[:k]

    def _get_similar_users(
        self,
        user_id: int,
        user_segment: int,
    ) -> Tuple[List[int], List[float]]:
        # take segment model:
        model = self.segment_model_map[user_segment]
        # find similar users:
        inner_user_id = model.users_mapping[user_id]
        sim_items_rates = model.user_knn.similar_items(
            inner_user_id, N=model.N_users
        )[
            1:
        ]  # exclude the same user
        # take rates lower than 1:
        sim = list(filter(lambda x: x[1] < 1, sim_items_rates))
        return (
            [model.users_inv_mapping[user] for user, _ in sim],
            [user_s for _, user_s in sim],
        )

    def _predict_by_model(
        self, user_id: int, user_segment: int, k: int
    ) -> List[int]:
        # get similar users (ids and scores):
        sim_users, sim_score = self._get_similar_users(user_id, user_segment)
        # prepare df to sort items of similar users:
        model = self.segment_model_map[user_segment]
        sim_users_items = model.watched.loc[sim_users]
        sim_users_items["sim"] = sim_score
        # evaluate score:
        sim_users_items = (
            # items of similar users:
            sim_users_items.explode("item_id")
            .reset_index()
            .rename(columns={"user_id": "sim_user_id"})
            .drop_duplicates(["item_id"], keep="first")
            # idf of items of similar users:
            .merge(
                model.item_idf, left_on="item_id", right_on="index", how="left"
            )
        )
        # final score:
        sim_users_items["score"] = (
            sim_users_items["sim"] * sim_users_items["idf"]
        )
        # sort by score:
        sim_users_items = sim_users_items.sort_values(
            ["score"], ascending=False
        )
        recs = sim_users_items["item_id"].iloc[:k].tolist()
        # complete with popular:
        if len(recs) < k:
            pop = list(
                filter(lambda x: x not in recs, self._predict_popular(k))
            )
            recs = (recs + pop)[:k]
        return recs

    def warmup(self, users_ids: List[int]) -> None:
        for user_id in users_ids:
            self.predict(user_id, k=self.warmup_k)


def read_dill(filepath: str) -> Any:
    with open(filepath, "rb") as f:
        data = dill.load(f)
    return data


class KNNModelConfig:
    def __init__(
        self,
        users_segment_map_path: str,
        sub_estimators_path: str,
        items_pop_ordered_path: str,
        warmup_users_path: Union[str, None],
    ):
        self.users_segment_map_path = users_segment_map_path
        self.sub_estimators_path = sub_estimators_path
        self.items_pop_ordered_path = items_pop_ordered_path
        self.warmup_users_path = warmup_users_path

        self.users_segment_map: Dict[int, int] = None
        self.sub_estimators: Dict[int, Any] = None
        self.items_pop_ordered: List[int] = None
        self.warmup_users: Union[List[int], None] = None

    def parse(self) -> None:
        self.users_segment_map = read_dill(self.users_segment_map_path)
        self.sub_estimators = read_dill(self.sub_estimators_path)
        self.items_pop_ordered = read_dill(self.items_pop_ordered_path)
        if self.warmup_users_path is not None:
            self.warmup_users = pd.read_csv(self.warmup_users_path)[
                "user_id"
            ].tolist()


class KNNModelInitializer:
    def __init__(
        self,
        config: KNNModelConfig,
    ):
        self.config = config

    def init_model(self) -> KNNModel:
        self.config.parse()
        model = KNNModel(
            user_segment_map=self.config.users_segment_map,
            segment_model_map=self.config.sub_estimators,
            pop_items=self.config.items_pop_ordered,
        )
        if self.config.warmup_users is not None:
            print("-" * 30)
            print("warmup started...")
            model.warmup(self.config.warmup_users)
        return model


# https://drive.google.com/file/d/1AVi5ztfkD0Ud0PZH0V8cm2KOZLpZYK8D/view?usp=sharing
knn_model_config = KNNModelConfig(
    users_segment_map_path="service/api/models/files/users_segment_map.dill",
    sub_estimators_path="service/api/models/files/segment_model_map.dill",
    items_pop_ordered_path="service/api/models/files/items_pop_ordered.dill",
    warmup_users_path=None,
)

knn_model_initializer = KNNModelInitializer(knn_model_config)
app_logger.info("kNN Model initialization...")
knn_model = knn_model_initializer.init_model()
