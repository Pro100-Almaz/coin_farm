from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import UserCreate, UserLogin, Subscribers, Subscriptions, UserPoints, UserLevel, User

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


router = APIRouter()


@router.post("/login_user")
async def read_user(user: UserLogin):
    user_data = await database.fetchrow(
        """
        UPDATE public.user
        SET last_login = $3
        WHERE telegram_id = $1 AND user_name = $2
        RETURNING user_id
        """, user.telegram_id, user.username, datetime.now()
    )

    user_id = int(user_data.get('user_id'))

    if not user_id:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"telegram_id": user.telegram_id, "username": user.username,
                                 "user_id": user_id})
    redis_database.set_user_token(user_id, token)

    return {"token": token, "user_id": user_id, "Status": "200"}
