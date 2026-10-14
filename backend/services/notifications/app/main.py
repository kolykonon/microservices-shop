import asyncio
import logging

from app.domain.handlers import on_user_registered
from app.infra.config import settings
from libs.events import OrderCreated, UserRegistered
from libs.rabbit import Rabbit
from services.notifications.app.domain.handlers import on_order_created


async def main():
    rabbit = await Rabbit.connect(settings.rabbit_url)
    try:
        await asyncio.gather(
            rabbit.consume(
                "notifications.user.registered", UserRegistered, on_user_registered
            ),
            rabbit.consume(
                "notifications.order.created", OrderCreated, on_order_created
            ),
        )
    finally:
        await rabbit.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
