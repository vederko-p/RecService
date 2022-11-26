from typing import List

from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from passlib.context import CryptContext


AVAILABLE_HASH = '$2b$12$uee7sjovrt.Pwxu1HR487ek7YzZjFh5XOk1fYau5CirLNP3gOWhI.'


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class BotRequest(BaseModel):
    model_name: str
    user_id: int
    k_recs: int


async def check_token(token: str):
    if not pwd_context.verify(token, AVAILABLE_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
    )
    

async def get_k_itmes(request: Request) -> int:
    return request.app.state.k_recs

    
async def get_bot_request(
    model_name: str,
    user_id: int,
    k_items: int = Depends(get_k_itmes),
    token: str = Depends(oauth2_scheme)
) -> BotRequest:
    await check_token(token)
    bot_request = BotRequest(
            model_name=model_name, user_id=user_id, k_recs=k_items)
    return bot_request
