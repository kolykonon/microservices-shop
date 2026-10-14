import time
from typing import Annotated

from fastapi import Depends

from app.infra.redis import RedisDep


class RefreshTokenStore:
    def __init__(self, redis: RedisDep):
        self.redis = redis

    @staticmethod
    def _to_str(value: bytes | str) -> str:
        return value.decode() if isinstance(value, bytes) else value

    @staticmethod
    def _token_key(jti: str) -> str:
        return f"auth:refresh:{jti}"

    @staticmethod
    def _user_key(user_id: str) -> bytes | str:
        return f"auth:user:{user_id}:refresh"

    async def save(self, user_id: str, jti: str, expires_at: int) -> None:
        now = int(time.time())
        ttl = expires_at - now
        if ttl <= 0:
            return

        user_key = self._user_key(user_id)
        async with self.redis.pipeline() as pipe:
            _ = pipe.set(self._token_key(jti), user_id, ex=ttl)
            _ = pipe.zadd(user_key, {jti: expires_at})
            _ = pipe.zremrangebyscore(user_key, 0, now)
            _ = pipe.expire(user_key, ttl)
            await pipe.execute()

    async def consume(self, jti: str) -> str | None:
        user_id = await self.redis.getdel(self._token_key(jti))
        if user_id:
            user_id = self._to_str(user_id)
            await self.redis.zrem(self._user_key(user_id), jti)
            return user_id
        else:
            return None

    async def revoke(self, user_id: str, jti: str) -> None:
        async with self.redis.pipeline() as pipe:
            _ = pipe.delete(self._token_key(jti))
            _ = pipe.zrem(self._user_key(user_id), jti)
            await pipe.execute()

    async def revoke_all(self, user_id: str) -> None:
        user_key = self._user_key(user_id)
        user_jtis = await self.redis.zrange(user_key, 0, -1)
        async with self.redis.pipeline() as pipe:
            for jti in user_jtis:
                if isinstance(jti, bytes):
                    jti = jti.decode()
                _ = pipe.delete(self._token_key(jti))  # pyright: ignore[reportArgumentType]
            _ = pipe.delete(user_key)
            await pipe.execute()


def get_token_store(
    redis: RedisDep,
) -> RefreshTokenStore:
    return RefreshTokenStore(redis)


TokenStoreDep = Annotated[RefreshTokenStore, Depends(get_token_store)]
