from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.v1 import router
from app.infra.config import settings
from app.infra.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncClient(base_url=settings.cart_catalog_url) as client:
        app.state.catalog_http_client = client
        yield
        await redis_client.aclose()


app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(router)
