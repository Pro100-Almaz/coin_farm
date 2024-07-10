from fastapi import APIRouter
from .miner import router as miner_router

router = APIRouter()

router.include_router(miner_router)

