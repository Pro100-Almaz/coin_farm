from sys import prefix

from fastapi import APIRouter
from .token import router as token_router
from .user import router as user_router
from .points import router as points_router
from .miner import router as miner_router

router = APIRouter()

router.include_router(user_router, prefix="/user")
router.include_router(token_router, prefix="/token")
router.include_router(points_router, prefix="/user")
router.include_router(miner_router, prefix="/user")

