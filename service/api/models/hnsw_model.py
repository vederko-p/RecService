import os
import typing as tp

import nmslib
import numpy as np


class HNSWModel:
    model_name = "hnsw_model"

    def __init__(
        self,
        index_time_params: tp.Dict[str, int],
        index_params: tp.Dict[str, tp.Union[int, nmslib.DataType]],
        embeddings: tp.Dict[str, np.array],
        maps: tp.Dict[str, tp.Dict[int, int]],
        pops: tp.List[int],
    ):
        # Params:
        self.index_time_params = index_time_params
        self.index_params = index_params
        # Embeddings:
        self.embeddings = embeddings
        # Index:
        self.index = nmslib.init(
            method=index_params["method"],
            space=index_params["space_name"],
            data_type=index_params["data_type"],
        )
        self.index.addDataPointBatch(embeddings["item_embeds_aug"])
        self.index.createIndex(index_time_params)
        # Query params:
        self.index.setQueryTimeParams(
            {"efSearch": index_time_params["efConstruction"]}
        )
        # Maps:
        self.user_map = maps["user_map"]
        self.user_map_inv = {v: k for k, v in maps["user_map"].items()}
        self.item_map = maps["item_map"]
        self.item_map_inv = {v: k for k, v in maps["item_map"].items()}
        # Popular items:
        self.pops = pops

    def predict(self, user_id: int, k: int = 10) -> tp.List[int]:
        in_user_id = self.user_map.get(user_id)
        print(f"in_user_id: {in_user_id}")
        if in_user_id is None:
            return self.pops[:k]
        else:
            query = self.embeddings["user_embeds_aug"][in_user_id]
            pred_items, _ = self.index.knnQuery(query, k=k)
            return list(map(self.item_map_inv.get, pred_items))


def init_configs(
    M_1: int,
    efC_1: int,
    num_threads_1: int,
    method_1: str,
    space_name_1: str,
    data_type_1: nmslib.DataType,
    user_embeds_aug_1: np.array,
    item_embeds_aug_1: np.array,
) -> tp.Tuple[
    tp.Dict[str, int],
    tp.Dict[str, tp.Union[int, nmslib.DataType]],
    tp.Dict[str, np.array],
]:
    index_time_params_0 = {
        "M": M_1,
        "indexThreadQty": num_threads_1,
        "efConstruction": efC_1,
    }
    index_params_0 = {
        "method": method_1,
        "space_name": space_name_1,
        "data_type": data_type_1,
    }
    embeddings_0 = {
        "user_embeds_aug": user_embeds_aug_1,
        "item_embeds_aug": item_embeds_aug_1,
    }
    return index_time_params_0, index_params_0, embeddings_0


# https://drive.google.com/file/d/130qQUY0jgCmzE8kI7q8uDNQgvJH8m8Vs/view?usp=sharing
files_path = "service/api/models/files"

# Load embeddings:
user_embeds_aug = np.load(os.path.join(files_path, "user_embeds_aug.npy"))
item_embeds_aug = np.load(os.path.join(files_path, "item_embeds_aug.npy"))

# Users/Items maps load:
items_map_np = np.load(os.path.join(files_path, "item_map.npy"))
items_map = {it_ex_it_in[0]: it_ex_it_in[1] for it_ex_it_in in items_map_np}
users_map_np = np.load(os.path.join(files_path, "user_map.npy"))
users_map = {us_ex_us_in[0]: us_ex_us_in[1] for us_ex_us_in in users_map_np}
maps = {"user_map": users_map, "item_map": items_map}

# Load popular:
popular_items_all = np.load(
    os.path.join(files_path, "popular_items.npy")
).tolist()
popular_items_all[:10]

# Init model:
a_best, b_best, c_best = init_configs(
    M_1=10,
    efC_1=20,
    num_threads_1=8,
    method_1="hnsw",
    space_name_1="negdotprod",
    data_type_1=nmslib.DataType.DENSE_VECTOR,
    user_embeds_aug_1=user_embeds_aug,
    item_embeds_aug_1=item_embeds_aug,
)
hnsw_model = HNSWModel(a_best, b_best, c_best, maps, popular_items_all)
