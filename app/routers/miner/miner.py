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
            t1.miner_id = t2.miner_id
        WHERE t1.active = true AND t2.user_id = $1;
        """, token_data.get("user_id")
    )

    if not miners:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find any miners.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"miners": miners, "Status": "200"}


@router.get("/miner/{miner_id}", dependencies=[Depends(JWTBearer())], tags=["Miner"])
async def get_miner(miner_id: int):
    miner = await database.fetchrow(
        """
        SELECT *
        FROM miners.miner
        WHERE active = true AND miner_id = %1
        """, miner_id
    )

    if not miner:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find any miner by id.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"miners": miner, "Status": "200"}


