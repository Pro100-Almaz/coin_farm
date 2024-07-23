import hashlib
import os
import urllib.parse
from cgitb import reset
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, status, Depends
from starlette.status import HTTP_409_CONFLICT

from .schemas import User, UserLevel

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


load_dotenv()
router = APIRouter()


@router.post("/login")
async def login_user(user: User):
    telegram_id = user.data.get("id")
    username = user.data.get("username")

    user_data = await database.fetchrow(
        """
        UPDATE public.user
        SET last_login = $3
        WHERE telegram_id = $1 AND user_name = $2
        RETURNING user_id, last_logout
        """, telegram_id, username, datetime.now()
    )

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(user_data.get('user_id'))

    user_points = await database.fetchrow(
        """
        SELECT *
        FROM public.points
        WHERE user_id = $1
        """, user_id
    )

    user_offline_period = (datetime.now() - user_data.get('last_logout')).total_seconds()

    if  user_offline_period < 10800:
        total_points = user_points.get('points_total') + int(user_offline_period *
                                                          (user_points.get('points_per_minute') // 60))
    else:
        total_points = user_points.get('points_total') + user_points.get('points_per_minute') * 180

    token = create_access_token({"telegram_id": telegram_id, "username": username,
                                 "user_id": user_id})
    redis_database.set_user_token(user_id, token)

    return {"token": token, "user_id": user_id, "Status": "200", "username": username, "total_points": total_points}

@router.post("/create")
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

        hashed_link = "https://t.me/practically_bot?start=refId" + str(telegram_id)

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


@router.post("/logout", dependencies=[Depends(JWTBearer())], tags=["default"])
async def logout_user():
    return True


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


@router.get("/get_level_list", tags=["level"])
async def get_level_list():
    result = await database.fetch(
        """
        SELECT *
        FROM public.level_list
        """
    )

    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no list of levels.")

    return {"Status": 200, "result": result}


@router.patch("/upgrade_level", tags=["level"])
async def upgrade_level(user_data: UserLevel, token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        UPDATE public.level
        SET level = $2
        WHERE user_id = $1
        """, token_data.get("user_id"), user_data.new_user_lvl
    )

    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no level id in level list.")

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

    if not result:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no such user.")

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
