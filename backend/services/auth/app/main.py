import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.v1 import router
from app.infra.config import settings
from app.infra.outbox_relay import run_outbox_relay
from app.infra.redis import redis_client
from libs.rabbit import Rabbit


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rabbit = await Rabbit.connect(settings.rabbit_url)
    relay = asyncio.create_task(run_outbox_relay(app.state.rabbit))
    yield
    relay.cancel()
    with suppress(asyncio.CancelledError):
        await relay
    await app.state.rabbit.close()
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
register_exception_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
