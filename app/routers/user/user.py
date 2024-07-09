from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from asyncpg.exceptions import UniqueViolationError

from .schemas import UserCreate, UserLogin
from app.utils import create_access_token

from app.database import database


router = APIRouter()


@router.post("/login_user")
async def read_user(user: UserLogin):
    user_data = await database.fetchrow(
        """
        SELECT *
        FROM public.user
        WHERE telegram_id = $1 AND user_name = $2
        """, user.telegram_id, user.username
    )

    if not user:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = create_access_token({"telegram_id": user.telegram_id, "username": user.username})

    return {"token": payload, "user": user, "Status": "200"}

@router.post("/create_user")
async def create_user(new_user: UserCreate):
    print(new_user.data)
    telegram_id = new_user.data.get("id")
    telegram_username = new_user.data.get("username")

    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid telegram_id"
        )

    try:
        user = await database.fetch(
            """
            INSERT INTO public.user (telegram_id, user_name, last_login, sign_up_date)
            VALUES ($1, $2, $3, $4)
            """, telegram_id, telegram_username, datetime.now(), datetime.now()
        )
    except UniqueViolationError:
        return HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"telegram_id": telegram_id, "username": telegram_username})

    return {"Status": 201, "user": user, "token": token}
