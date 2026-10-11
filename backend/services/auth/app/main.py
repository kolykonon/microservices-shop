from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.v1 import router
from app.infra.redis import redis_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
register_exception_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
