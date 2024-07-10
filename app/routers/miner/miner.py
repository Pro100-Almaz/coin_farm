from fastapi import APIRouter, HTTPException, status, Depends

from app.auth_bearer import JWTBearer
from app.database import database


router = APIRouter()


@router.get("/miners", dependencies=[Depends(JWTBearer())])
async def get_miners():
    miners = await database.fetch(
        """
        SELECT *
        FROM miners.miner
        WHERE active = true
        """
    )

    if not miners:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find any miners.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"miners": miners, "Status": "200"}

@router.get("/miner/{miner_id}", dependencies=[Depends(JWTBearer())])
async def get_miners(miner_id: int):
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


