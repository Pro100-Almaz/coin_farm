from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import User

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


router = APIRouter()


@router.post("/buy_miner/{miner_id}", dependencies=[Depends(JWTBearer())])
async def read_user(user: User, miner_id: int):
    #
    condition_check = await database.fetchrow(
        """
        
        """
    )

    miner = await database.fetchrow(
        """
        SELECT miner_id
        FROM miners.miner
        WHERE miner_id = $1 AND active = true
        """
    )

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
