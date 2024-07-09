from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import UserCreate, UserLogin, Subscribers, Subscriptions, UserPoints, UserLevel

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database


router = APIRouter()


@router.post("/login_user")
async def read_user(user: UserLogin):
    user_data = await database.fetchrow(
        """
        UPDATE public.user
        SET last_login = $3
        WHERE telegram_id = $1 AND user_name = $2
        RETURNING *
        """, user.telegram_id, user.username, datetime.now()
    )

    if not user_data:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = create_access_token({"telegram_id": user.telegram_id, "username": user.username})

    return {"token": payload, "user": user_data, "Status": "200"}

@router.post("/create_user")
async def create_user(new_user: UserCreate):
    telegram_id = new_user.data.get("id")
    telegram_username = new_user.data.get("username")
    first_name: str = new_user.data.get("first_name")
    last_name: str = new_user.data.get("last_name")
    language_code: str = new_user.data.get("language_code")

    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid telegram_id"
        )

    try:
        result = await database.fetch(
            """
            INSERT INTO public.user (telegram_id, user_name, last_login, sign_up_date, first_name, last_name, language_code)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING user_id
            """, telegram_id, telegram_username, datetime.now(), datetime.now(), first_name, last_name, language_code
        )
        user_id = int(result[0].get('user_id'))

        await database.execute(
            """
            INSERT INTO public.points (user_id, points_total, points_per_hour, next_rise) VALUES ($1, 0, 0, $2);
            """, user_id, datetime.now()
        )
        await database.execute(
            """
            INSERT INTO public.subscriptions (user_id, count, list_of_ids) VALUES ($1, 0, ARRAY[]::integer[]);
            """, user_id
        )
        await database.execute(
            """
            INSERT INTO public.subscribers (user_id, count, list_of_ids) VALUES ($1, 0, ARRAY[]::integer[]);
            """, user_id
        )
        await database.execute(
            """
            INSERT INTO public.level (user_id, level, current_percent) VALUES ($1, 1, 0);
            """, user_id
        )
    except Exception as e:
        print(e)
        return HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"telegram_id": telegram_id, "username": telegram_username})

    return {"Status": 201, "user_id": user_id, "token": token}

@router.get("/get_subscriptions", dependencies=[Depends(JWTBearer())], tags=["subscriptions"])
async def get_subscriptions(subs: Subscriptions):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.subscriptions
        WHERE user_id = $1
        """, subs.user_id
    )

    return result

@router.get("/get_subscribers", dependencies=[Depends(JWTBearer())], tags=["subscribers"])
async def get_subscribers(subs: Subscribers):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.subscriptions
        WHERE user_id = $1
        """, subs.user_id
    )

    return result

@router.get("/get_points", dependencies=[Depends(JWTBearer())], tags=["points"])
async def get_points(user: UserPoints):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.points
        WHERE user_id = $1
        """, user.user_id
    )

    return result

@router.get("/get_level", dependencies=[Depends(JWTBearer())], tags=["level"])
async def get_level(user: UserLevel):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.level
        WHERE user_id = $1
        """, user.user_id
    )

    return result