import uvicorn
import json
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import database
from fastapi.middleware.cors import CORSMiddleware

from app.webhook import router as webhook_router
from app.images import router as image_router
from app.routers import user as user_router
from app.routers import miner as miner_router

from .logger import logger

app = FastAPI()
logger.info("Start FastAPI app...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path == "/docs" or request.url.path == "/openapi.json":
            return response

        response_body = [chunk async for chunk in response.body_iterator]
        response_body_bytes = b''.join(response_body)

        new_response = Response(
            content=response_body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        try:
            response_body_str = response_body_bytes.decode('utf-8')
            response_body_json = json.loads(response_body_str)
            logger.info(f"{request.url.path} -- {request.method}, "
                        f"Response Body: {json.dumps(response_body_json, indent=2)}")
        except Exception as e:
            logger.error(f"{request.url.path} -- {request.method}, Failed to decode or log response body: {e}")

        return new_response


app.add_middleware(LogMiddleware)

app.include_router(image_router)
app.include_router(user_router.router)
app.include_router(miner_router.router)
app.include_router(webhook_router, prefix="/webhook")



@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
