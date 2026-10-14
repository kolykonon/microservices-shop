from app.infra.cart_repo import CartRepo
from app.infra.config import settings
from app.infra.redis import redis_client
from libs.events import OrderCreated


async def on_order_created(event: OrderCreated) -> None:
    await CartRepo(redis_client, settings.cart_ttl_seconds).clear_cart(event.user_id)
