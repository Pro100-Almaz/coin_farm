import hashlib
import os
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import UserCreate, UserLogin

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


load_dotenv()
router = APIRouter()


def create_hashed_link(user_id, username, telegram_id, hash_length=20):
    concatenated_string = f"{user_id}-{username}-{telegram_id}"

    hashed_value = hashlib.sha256(concatenated_string.encode()).hexdigest()
    truncated_hash = hashed_value[:hash_length]

    base_link = str(os.getenv('SECRET_KEY')) + "/referral_link/"
    hashed_link = f"{base_link}{urllib.parse.quote(truncated_hash)}"

    return hashed_link

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

        hashed_link = create_hashed_link(user_id, telegram_username, telegram_id)

        if hashed_link:
            await database.execute(
                """
                UPDATE public.user 
                SET referral_link = $1
                WHERE user_id = $2
                """, hashed_link, user_id
            )

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

    token = create_access_token({"telegram_id": telegram_id, "username": telegram_username, "user_id": user_id})
    redis_database.set_user_token(user_id, token)

    return {"Status": 201, "user_id": user_id, "token": token}

# @router.get("/get_user", dependencies=[Depends(JWTBearer())], tags=["subscriptions"])
# async def get_subscriptions(user_id: int):
#     result = await database.fetchrow(
#         """
#         SELECT *
#         FROM public.user
#         WHERE user_id = $1
#         """, user_id
#     )
#
#     return {"Status": 200, "result": result}

@router.get("/get_user/{user_id}", dependencies=[Depends(JWTBearer())], tags=["get_user"])
async def get_user(user_id: int):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.user
        WHERE user_id = $1
        """, user_id
    )

    return {"Status": 200, "result": result}


@router.get("/get_friend/{user_id}", dependencies=[Depends(JWTBearer())], tags=["User by which referral link, client "
                                                                                "was called"])
async def get_linked_friend(user_id: int):
    result = await database.fetchrow(
        """
        SELECT friend_id
        FROM public.friend_to
        WHERE user_id = $1
        """, user_id
    )

    return {"Status": 200, "result": result}


@router.get("/get_friends/{user_id}", dependencies=[Depends(JWTBearer())], tags=["Clients which entered by referral "
                                                                                 "link of the user"])
async def get_subscribed_friends(user_id: int):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.friend_for
        WHERE user_id = $1
        """, user_id
    )

    return {"Status": 200, "result": result}


@router.get("/get_points/{user_id}", dependencies=[Depends(JWTBearer())], tags=["points"])
async def get_points(user_id: int):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.points
        WHERE user_id = $1
        """, user_id
    )

    return {"Status": 200, "result": result}


@router.get("/get_level/{user_id}", dependencies=[Depends(JWTBearer())], tags=["level"])
async def get_level(user_id: int):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.level
        WHERE user_id = $1
        """, user_id
    )

    return {"Status": 200, "result": result}