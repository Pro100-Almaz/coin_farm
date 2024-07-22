from typing import Dict

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import UserPoints

from app.auth_bearer import JWTBearer
from app.database import database


router = APIRouter()


@router.patch("/update_points", tags=["points"])
async def update_points(data: UserPoints, token_data: Dict = Depends(JWTBearer())):
    try:
        await database.execute(
            """
            UPDATE public.points
            SET points_total = $2
            WHERE user_id = $1 
            """, token_data.get("user_id"), data.gain_points
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not validate credentials"
        )

    return {"user_id": token_data.get("user_id"), "Status": "204", "details": "Data updated successfully."}


@router.get("/claim_miner_points", tags=["points"])
async def claim_miner_points(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetchrow(
        """
        SELECT *
        FROM public.points
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": 200, "result": result}


@router.post("/upgrade_tap", tags=["tap"])
async def upgrade_tap(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetch(
        """
        UPDATE public.points
        SET points_per_click = points_per_click + 1, upgrade_price = upgrade_price * 2
        WHERE user_id = $1
        RETURNING *
        """
    )

    return {"Status": 200, "result": result}


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
