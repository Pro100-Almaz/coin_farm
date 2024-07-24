from datetime import datetime, timedelta
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


@router.post("/upgrade_tap", tags=["tap"])
async def upgrade_tap(token_data: Dict = Depends(JWTBearer())):
    result = await database.fetch(
        """
        UPDATE public.points
        SET points_per_click = points_per_click + 1, upgrade_price = upgrade_price * 2
        WHERE user_id = $1
        RETURNING *
        """, token_data.get('user_id')
    )

    return {"Status": 200, "result": result}


@router.get("/request_daily_bonus", tags=["points"])
async def request_daily_points(token_data: Dict = Depends(JWTBearer())):
    user_id = token_data.get("user_id")

    last_request = await database.fetchrow(
        """
        SELECT last_bonus_request, bonus_id
        FROM public."user"
        WHERE user_id = $1
        """, user_id
    )

    last_request = last_request.get("last_bonus_request")
    next_bonus_id = 2
    user_status = "took"

    if (last_request.date() + timedelta(days=1)) == datetime.today().date():
        user_status = "streak"
        try:
            user_bonus = await database.fetchrow(
                """
                WITH ordered_ids AS (
                    SELECT
                        bonus_id,
                        ROW_NUMBER() OVER (ORDER BY bonus_id) AS row_num,
                        COUNT(*) OVER () AS total_count,
                        points
                    FROM public.bonus
                )
                SELECT
                    CASE
                        WHEN row_num = total_count THEN (SELECT MIN(bonus_id) FROM public.bonus)
                        ELSE (SELECT bonus_id FROM public.bonus WHERE bonus_id > $1 ORDER BY bonus_id LIMIT 1)
                    END AS next_id,
                    points
                FROM
                    ordered_ids
                WHERE
                    bonus_id = $1;
                """, last_request.get("bonus_id")
            )
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not get bonus points, please try later.")

        next_bonus_id = user_bonus.get("next_id")
        bonus_points = user_bonus.get("points")
    elif last_request.date() == datetime.today().date():
        bonus_points = 0
    else:
        try:
            user_bonus = await database.fetchrow(
                """
                SELECT points
                FROM public.bonus
                WHERE bonus_id = 1
                """
            )
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not get bonus points, please try later.")

        user_status = "non-streak"
        bonus_points = user_bonus.get("points")

    await database.execute(
        """
        UPDATE public."user"
        SET bonus_id = $1
        WHERE user_id = $2
        """, next_bonus_id, user_id
    )

    return {"Status": 200, "bonus_points": bonus_points, "user_status": user_status}



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
