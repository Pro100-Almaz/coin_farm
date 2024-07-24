from typing import Dict

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas import UserPoints

from app.auth_bearer import JWTBearer
from app.database import database


router = APIRouter()


@router.get("/friends", tags=["referral"])
async def get_friends(token_data: Dict = Depends(JWTBearer())):
    user_friends = await database.fetch(
        """
        SELECT *
        FROM public.user_friends_history
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    farmed_points = 0

    for record in user_friends:
        if not record.get("requested"):
            farmed_points += record.get("points")

    await database.execute(
        """
        UPDATE public.user_friends_history
        SET requested = true
        WHERE user_id = $1
        """, token_data.get("user_id")
    )

    return {"Status": "200", "friends": user_friends, "farmed_points": farmed_points}
