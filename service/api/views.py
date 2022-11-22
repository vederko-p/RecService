from typing import List, Union

from fastapi import APIRouter, FastAPI, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError, ModelNotFoundError
from service.log import app_logger

from service.api.models.models_base import models_base


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if models_base.check_model(model_name):
        model = models_base.init_model(model_name)
    else:
        raise ModelNotFoundError(
            status_code=404, detail=f'Model {model_name} not found')
            # TODO: Use status.HTTP_404_NOT_FOUND instead of 404
            #       (from fastapi import status)
    
    reco = model.predict(request.app.state.k_recs)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
