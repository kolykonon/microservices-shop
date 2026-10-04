from collections.abc import AsyncIterator

from app.infra.config import settings
from redis.asyncio import Redis

redis_client = Redis.from_url(settings.redis_url)


async def get_redis() -> AsyncIterator[Redis]:
    async with redis_client as redis:
        yield redis
