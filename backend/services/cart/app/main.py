import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.v1 import router
from app.domain.handlers import on_order_created
from app.infra.config import settings
from app.infra.redis import redis_client
from libs.events import OrderCreated
from libs.rabbit import Rabbit


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AsyncClient(base_url=settings.cart_catalog_url) as client:
        app.state.rabbit = await Rabbit.connect(settings.rabbit_url)
        consumer = asyncio.create_task(
            app.state.rabbit.consume(
                "cart.order_created", OrderCreated, on_order_created
            )
        )
        app.state.catalog_http_client = client
        yield
        consumer.cancel()
        await app.state.rabbit.close()
        await redis_client.aclose()


app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(router)
