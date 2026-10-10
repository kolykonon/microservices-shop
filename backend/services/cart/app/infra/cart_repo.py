from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.domain.schemas.cart import Cart, CartItem
from app.infra.config import settings
from app.infra.redis import RedisDep


class CartRepo:
    def __init__(
        self,
        redis_client: Redis,
        cart_ttl: int,
    ) -> None:
        self._redis_client: Redis = redis_client
        self.cart_ttl: int = cart_ttl

    @staticmethod
    def _get_cart_key(user_id: int) -> str:
        return f"cart:{user_id}"

    async def add_to_cart(
        self,
        user_id: int,
        data: CartItem,
    ) -> int:
        cart_key = self._get_cart_key(user_id)
        async with self._redis_client.pipeline() as pipe:
            _ = pipe.hincrby(
                name=cart_key,
                key=str(data.product_id),
                amount=data.quantity,
            )
            _ = pipe.expire(
                name=cart_key,
                time=self.cart_ttl,
            )
            new_quantity, _ = await pipe.execute()
        return int(new_quantity)

    async def set_quantity(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
    ) -> bool:
        cart_key = self._get_cart_key(user_id)
        if not await self._redis_client.hexists(cart_key, str(product_id)):
            return False
        async with self._redis_client.pipeline() as pipe:
            _ = pipe.hset(
                name=cart_key,
                key=str(product_id),
                value=quantity,
            )
            _ = pipe.expire(
                name=cart_key,
                time=self.cart_ttl,
            )
            await pipe.execute()
        return True

    async def clear_cart(
        self,
        user_id: int,
    ) -> bool:
        cart_key = self._get_cart_key(user_id)
        deleted = await self._redis_client.delete(cart_key)
        return bool(deleted)

    async def remove_from_cart(
        self,
        user_id: int,
        product_id: int,
    ) -> bool:
        cart_key = self._get_cart_key(user_id)
        async with self._redis_client.pipeline() as pipe:
            _ = pipe.hdel(cart_key, str(product_id))
            _ = pipe.expire(
                name=cart_key,
                time=self.cart_ttl,
            )
            deleted, _ = await pipe.execute()
        return bool(deleted)

    async def get_cart(self, user_id: int) -> Cart:
        cart_key = self._get_cart_key(user_id)
        async with self._redis_client.pipeline() as pipe:
            _ = pipe.hgetall(cart_key)
            _ = pipe.expire(
                name=cart_key,
                time=self.cart_ttl,
            )
            result, _ = await pipe.execute()
        items = [
            CartItem(
                product_id=int(product_id),
                quantity=int(quantity),
            )
            for product_id, quantity in result.items()
            if product_id.isdigit() and quantity.isdigit() and int(quantity) > 0
        ]
        return Cart(items=items)


def get_cart_repo(rc: RedisDep) -> CartRepo:
    return CartRepo(rc, settings.cart_ttl_seconds)


CartRepoDep = Annotated[CartRepo, Depends(get_cart_repo)]
