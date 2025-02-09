from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

AVAILABLE_HASH = "$2b$12$uee7sjovrt.Pwxu1HR487ek7YzZjFh5XOk1fYau5CirLNP3gOWhI."


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class BotRequest(BaseModel):
    model_name: str
    user_id: int
    k_recs: int


def check_token(token: str) -> bool:
    return pwd_context.verify(token, AVAILABLE_HASH)


async def get_k_items(request: Request) -> int:
    return request.app.state.k_recs


async def get_bot_request(
    model_name: str,
    user_id: int,
    k_items: int = Depends(get_k_items),
    token: str = Depends(oauth2_scheme),
) -> BotRequest:
    verified = check_token(token)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    bot_request = BotRequest(
        model_name=model_name, user_id=user_id, k_recs=k_items
    )
    return bot_request
