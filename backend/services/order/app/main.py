from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.v1.order import router as order_router
from app.infra.config import settings
from libs.rabbit import Rabbit


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncClient(base_url=settings.order_cart_url) as client:
        app.state.rabbit = await Rabbit.connect(settings.rabbit_url)
        app.state.cart_http_client = client
        yield
        await app.state.rabbit.close()


app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(router=order_router, prefix="/api/v1")


@app.get(path="/health")
def health():
    return {"status": "ok"}
