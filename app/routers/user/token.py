from fastapi import APIRouter, HTTPException, status
import jwt

from .schemas import Token
from app.utils import create_access_token, SECRET_KEY, ALGORITHM

from app.database import database, redis_database


router = APIRouter()


@router.post("/refresh_token")
async def refresh_access_token(token = Token):
    token_old = redis_database.get_user_token(token.user_id)
    try:
        payload = jwt.decode(token_old, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("telegram_id") == token.telegram_id and \
            payload.get("username") == token.username and \
            payload.get("user_id") == token.user_id:
            token = create_access_token({"telegram_id": token.telegram_id, "username": token.username,
                                         "user_id": token.user_id})
            redis_database.set_user_token(token.user_id, token)
        else:
            return HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"Status": 200, "token": token}
