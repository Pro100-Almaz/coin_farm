import uvicorn
from fastapi import FastAPI
from app.database import database
from fastapi.middleware.cors import CORSMiddleware

from app.webhook import router as webhook_router
from app.routers import user as user_router
from app.images import router as image_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(image_router)
app.include_router(webhook_router, prefix="/webhook")



@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
