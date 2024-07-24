from typing import Dict

from fastapi import APIRouter, HTTPException, status, Depends

from app.auth_bearer import JWTBearer
from app.database import database


router = APIRouter()


@router.get("/miners", tags=["Miner"])
async def get_miners(token_data: Dict = Depends(JWTBearer())):
    miners = await database.fetch(
        """
        SELECT 
            COALESCE(t2.next_price, t1.price) AS price,
            COALESCE(t2.next_point_per_hour, t1.point_per_hour) AS point_per_hour,
            COALESCE(t2.level, t1.level) AS level,
            title,
            description,
            photo
        FROM 
            miners.miner t1
        LEFT JOIN 
            miners.user_miner t2 
        ON 
            t1.miner_id = t2.miner_id AND t2.user_id = $1
        WHERE t1.active = true;
        """, token_data.get("user_id")
    )

    if not miners:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find any miners."
        )

    return {"miners": miners, "Status": "200", "length": len(miners)}


@router.get("/miners/{miner_type}", tags=["Miner"])
async def get_miner(token_data: Dict = Depends(JWTBearer()), miner_type: str = None):
    print(token_data.get("user_id"))
    miners = await database.fetch(
        """
        SELECT 
            COALESCE(t2.next_price, t1.price) AS price,
            COALESCE(t2.next_point_per_hour, t1.point_per_hour) AS point_per_hour,
            COALESCE(t2.level, t1.level) AS level,
            title,
            description,
            photo
        FROM 
            miners.miner t1
        LEFT JOIN 
            miners.user_miner t2 
        ON 
            t1.miner_id = t2.miner_id AND t2.user_id = $1
        WHERE t1.active = true AND t1.type = $2;
        """, token_data.get("user_id"), miner_type
    )

    if not miners:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find any miners."
        )

    return {"miners": miners, "Status": "200", "length": len(miners)}

@router.post("/miner/buy/{miner_id}", tags=["Miner"])
async def buy_miner(miner_id: int, token_data: Dict = Depends(JWTBearer())):
    # condition format: condition:value
    miner = await database.fetchrow(
        """
        SELECT miner_id
        FROM miners.miner
        WHERE miner_id = $1 AND active = true
        """, miner_id
    )

    user_id = token_data.get("user_id")

    miner_condition = miner.get("condition")
    if miner_condition:
        condition, required_value = miner_condition.split(":")

        if condition == "minimum_point":
            user_points = await database.fetchrow(
                """
                SELECT points_total
                FROM public.points
                WHERE user_id = $1
                """, user_id
            )

            if user_points < int(required_value):
                raise HTTPException(
                    status_code=status.HTTP_412_PRECONDITION_FAILED,
                    detail="User points is not facing required amount!"
                )

        elif condition == "minimum_friends":
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
                    detail="User friends is not facing required amount!"
                )

    next_price = int(miner.get("price") + (miner.get("price") * miner.get("rise_coef_price") / 100))
    next_points_per_hour = int(miner.get("point_per_hour") + (miner.get("point_per_hour") *
                                                              miner.get("rise_coef_income") / 100))

    await database.execute(
        """
        INSERT INTO miners.user_miner (user_id, miner_id, next_price, point_per_hour, next_point_per_hour)
        VALUES ($1, $2, $3, $5, $6);
        """, user_id, miner.get("miner_id"),  next_price, miner.get("point_per_hour"), next_points_per_hour
    )

    await database.execute(
        """
        UPDATE public.points
        SET points_per_hour = points_per_hour + $2
        WHERE user_id = $1;
        """, user_id, miner.get("point_per_hour")
    )

    return {"Status": "200", "Details": "Miner successfully added into user account!"}
