from collections.abc import AsyncIterator

from redis.asyncio import Redis

from app.infra.config import settings

redis_client = Redis.from_url(settings.redis_url)


async def get_redis() -> AsyncIterator[Redis]:
    async with redis_client as redis:
        yield redis
