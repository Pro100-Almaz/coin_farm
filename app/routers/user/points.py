from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import UserPoints

from app.utils import create_access_token
from app.auth_bearer import JWTBearer
from app.database import database, redis_database


router = APIRouter()


@router.patch("/update_points", dependencies=[Depends(JWTBearer())], tags=["points"])
async def update_points(data: UserPoints):
    try:
        await database.execute(
            """
            UPDATE public.points
            SET points_total = $2
            WHERE user_id = $1 
            """, data.user_id, data.gain_points
        )
    except:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": data.user_id, "Status": "204", "details": "Data updated successfully."}

# @router.patch("/add_points_per_hour", dependencies=[Depends(JWTBearer())])
# async def update_points(data: UserPoints):
#     try:
#         await database.execute(
#             """
#             UPDATE public.points
#             SET points_total = $2
#             WHERE user_id = $1
#             """, data.user_id, data.gain_points
#         )
#     except:
#         return HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     return {"user_id": data.user_id, "Status": "204", "details": "Data updated successfully."}
