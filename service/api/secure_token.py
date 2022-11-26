from typing import List

from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel


AVAILABLE_TOKENS = [
    'test_token_23'
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class BotRequest(BaseModel):
    model_name: str
    user_id: int
    k_recs: int


async def check_token(token, available_tokens: List[str]):
    if token not in available_tokens:
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
    check_token(token, AVAILABLE_TOKENS)
    bot_request = BotRequest(
            model_name=model_name, user_id=user_id, k_recs=k_items)
    return bot_request
