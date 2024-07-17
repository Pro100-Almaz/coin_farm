import hashlib
import os
import urllib.parse
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import User, UserLevel

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


load_dotenv()
router = APIRouter()


def create_hashed_link(user_id, username, telegram_id, hash_length=30):
    concatenated_string = f"{user_id}-{username}-{telegram_id}"

    hashed_value = hashlib.sha256(concatenated_string.encode()).hexdigest()
    truncated_hash = hashed_value[:hash_length]

    base_link = str(os.getenv('BASE_URL')) + "/referral_link/"
    hashed_link = f"{base_link}{urllib.parse.quote(truncated_hash)}"

    return hashed_link

@router.post("/login_user")
async def login_user(user: User):
    telegram_id = user.data.get("id")
    username = user.data.get("username")

    user_data = await database.fetchrow(
        """
        UPDATE public.user
        SET last_login = $3
        WHERE telegram_id = $1 AND user_name = $2
        RETURNING user_id
        """, telegram_id, username, datetime.now()
    )

    user_id = int(user_data.get('user_id'))

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"telegram_id": telegram_id, "username": username,
                                 "user_id": user_id})
    redis_database.set_user_token(user_id, token)

    return {"token": token, "user_id": user_id, "Status": "200", "username": username}

@router.post("/create_user")
async def create_user(new_user: User):
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
            INSERT INTO public.friend_for (user_id, count, list_of_ids) VALUES ($1, 0, ARRAY[]::integer[]);
            """, user_id
        )
        await database.execute(
            """
            INSERT INTO public.friend_to (user_id, friend_id) VALUES ($1, NULL);
            """, user_id
        )
        await database.execute(
            """
            INSERT INTO public.level (user_id, level, current_percent) VALUES ($1, 1, 0);
            """, user_id
        )
        await database.execute(
            """
            INSERT INTO public.stamina (user_id) VALUES ($1);
            """, user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    token = create_access_token({"telegram_id": telegram_id, "username": telegram_username, "user_id": user_id})
    redis_database.set_user_token(user_id, token)

    return {"Status": 201, "user_id": user_id, "token": token, "username": telegram_username}


@router.get("/{user_id}", dependencies=[Depends(JWTBearer())], tags=["default"])
async def get_user(user_id: int):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.user
        WHERE user_id = $1
        """, user_id
    )

    return {"Status": 200, "result": result}


@router.get("/get_friend", tags=["user by which referral link, client was called"])
async def get_linked_friend(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT friend_id
        FROM public.friend_to
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}


@router.get("/get_friends", tags=["clients which entered by referral link of the user"])
async def get_subscribed_friends(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.friend_for
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}


@router.get("/get_points", tags=["points"])
async def get_points(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.points
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}


@router.get("/get_level", tags=["level"])
async def get_level(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.level lvl
        LEFT JOIN public.level_list lvl_l ON lvl.level = lvl_l.level_id
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}


@router.patch("/upgrade_level", tags=["level"])
async def upgrade_level(user_data: UserLevel, token_data: Dict = Depends(JWTBearer())):
    percent = (user_data.user_points // user_data.max_points) * 100
    if percent > 100:
        level_upgrade = user_data.current_lvl + (percent // 100)
        percent = percent % 100
    else:
        level_upgrade = user_data.current_lvl

    result = await database.fetchrow(
        """
        UPDATE public.level
        SET level = $2, current_percent = $3
        WHERE user_id = $1
        """, token_data.get("user_id"), percent, level_upgrade
    )

    return {"Status": 200, "result": result}


@router.get("/stamina", tags=["stamina"])
async def get_stamina(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.stamina
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}


@router.post("/upgrade_stamina", tags=["stamina"])
async def upgrade_stamina(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetch(
        """
        UPDATE public.stamina
        SET current_stamina = current_stamina + 500, upgrade_price = upgrade_price * 2
        WHERE user_id = $1
        RETURNING *
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}
