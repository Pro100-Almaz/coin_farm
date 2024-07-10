from fastapi import APIRouter

router = APIRouter()

router.include_router(user_router, prefix="/user")
router.include_router(token_router, prefix="/token")

