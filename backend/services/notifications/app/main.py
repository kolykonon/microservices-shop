import asyncio
import logging

from app.domain.handlers import on_user_registered
from app.infra.config import settings
from libs.events import UserRegistered
from libs.rabbit import Rabbit


async def main():
    rabbit = await Rabbit.connect(settings.rabbit_url)
    try:
        await rabbit.consume(
            "notifications.user_registered", UserRegistered, on_user_registered
        )
    finally:
        await rabbit.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
