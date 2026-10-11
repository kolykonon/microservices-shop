from collections.abc import AsyncIterator
from typing import Annotated

from redis.asyncio import Redis

from app.infra.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> AsyncIterator[Redis]:
    yield redis_client


RedisDep = Annotated[Redis, settings.redis_url]
