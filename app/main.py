from typing import Union
from fastapi import FastAPI
from app.database import database
from app.routers import items

from app.webhook import router as webhook_router

app = FastAPI()
app.include_router(webhook_router, prefix="/webhook")


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None):
    return {"item_id": item_id, "q": q}