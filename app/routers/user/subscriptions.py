from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from asyncpg.exceptions import UniqueViolationError

from .schemas import Subscriptions
from app.utils import create_access_token, verify_token, SECRET_KEY, ALGORITHM

from app.database import database
from app.auth_bearer import JWTBearer


router = APIRouter()


@router.post("/get_subscriptions", dependencies=[Depends(JWTBearer())], tags=["subscriptions"])
async def get_subscriptions(subs: Subscriptions):


@router.post("/get_subscribers")
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
