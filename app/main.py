from typing import Union
from fastapi import FastAPI
from app.database import database
from fastapi.middleware.cors import CORSMiddleware

from app.webhook import router as webhook_router
from app.routers import user as user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(webhook_router, prefix="/webhook")


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None):
    return {"item_id": item_id, "q": q}


@app.post("/send-data")
async def read_root(data: Union[dict, None]):
    print(data)
    return {}