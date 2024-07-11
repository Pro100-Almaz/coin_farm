from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from httpx import request

from .schemas import User

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


router = APIRouter()


@router.post("{user_id}/buy_miner/{miner_id}", dependencies=[Depends(JWTBearer())], tags=["Miner"])
async def read_user(user_id: int, miner_id: int):
    # condition format: condition:value
    miner = await database.fetchrow(
        """
        SELECT miner_id
        FROM miners.miner
        WHERE miner_id = $1 AND active = true
        """, miner_id
    )

    miner_condition = miner.get("condition")
    if miner_condition:
        condition, required_value = miner_condition.split(":")

        if condition == "minimum_points":
            user_points = await database.fetchrow(
                """
                SELECT points_total
                FROM public.points
                WHERE user_id = $1
                """, user_id
            )

            if user_points < int(required_value):
                return HTTPException(
                    status_code=status.HTTP_412_PRECONDITION_FAILED,
                    detail="User points is not facing required amount!",
                    headers={},
                )

        elif condition == "minimum_followers":
            user_friends = await database.fetchrow(
                """
                SELECT count
                FROM public.friend_for
                WHERE user_id = $1
                """, user_id
            )

            if user_friends < int(required_value):
                return HTTPException(
                    status_code=status.HTTP_412_PRECONDITION_FAILED,
                    detail="User friends is not facing required amount!",
                    headers={},
                )

    next_price = int(miner.get("price") + (miner.get("price") * miner.get("rise_coef_price") / 100))
    next_points_per_hour = int(miner.get("point_per_hour") + (miner.get("point_per_hour") *
                                                              miner.get("rise_coef_income") / 100))

    await database.execute(
        """
        INSERT INTO miners.user_miner (user_id, miner_id, next_price, next_level, point_per_hour, next_point_per_hour)
        VALUES ($1, $2, $3, $4, $5, $6);
        """, user_id, miner.get("miner_id"),  next_price, 2, miner.get("point_per_hour"), next_points_per_hour
    )

    await database.execute(
        """
        UPDATE public.points
        SET points_per_hour = points_per_hour + $2
        WHERE user_id = $1;
        """, user_id, miner.get("point_per_hour")
    )

    return {"Status": "200", "Details": "Miner successfully added into user account!"}
