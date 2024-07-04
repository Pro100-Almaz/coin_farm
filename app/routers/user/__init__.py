from fastapi import APIRouter
from .token import router as token_router
from .user import router as user_router

router = APIRouter()

router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(token_router, prefix="/token", tags=["token"])