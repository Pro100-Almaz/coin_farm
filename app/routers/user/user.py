from datetime import datetime
from typing import Dict

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import User, UserLevel

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database
from app.logger import logger

load_dotenv()
router = APIRouter()


@router.post("/login")
async def login_user(user: User):
    telegram_id = user.data.get("id")
    username = user.data.get("username")

    user_data = await database.fetchrow(
        """
        UPDATE public.user
        SET last_login = $3, active = true
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
        accumulated_points = int(user_offline_period * (user_points.get('points_per_minute') // 60))
    else:
        accumulated_points = user_points.get('points_per_minute') * 180

    token = create_access_token({"telegram_id": telegram_id, "username": username,
                                 "user_id": user_id})
    redis_database.set_user_token(user_id, token)

    return {"token": token, "user_id": user_id, "Status": "200", "username": username,
            "accumulated_points": accumulated_points}


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


@router.get("/get_points", tags=["points"])
async def get_points(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT points_total, points_per_minute, points_per_click, click_upgrade_price
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
    user_id = token_data.get("user_id")

    try:
        await database.execute(
            """
            UPDATE public.user_friends_history AS ufh
            SET points = CASE
                                    WHEN ufh.tg_premium THEN rp.for_premium
                                    ELSE rp.for_standard
                         END
            FROM public.referral_points AS rp
            WHERE ufh.referred_id = $1 AND rp.lvl = $2
            """, user_id, user_data.new_user_lvl
        )
    except Exception as e:
        logger.error(f"Tried to add referral new points! User id: {user_id}")

    result = await database.fetchrow(
        """
        UPDATE public.level
        SET level = $2
        WHERE user_id = $1
        """, user_id, user_data.new_user_lvl
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


@router.get("/refresh_stamina", tags=["stamina"])
async def refresh_stamina(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetch(
        """
        UPDATE public.stamina
        SET current_stamina = current_stamina + 500, upgrade_price = upgrade_price * 2
        WHERE user_id = $1
        RETURNING *
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}
