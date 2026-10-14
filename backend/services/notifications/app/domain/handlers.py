import logging

from libs.events import OrderCreated, UserRegistered

logger = logging.getLogger(__name__)


async def on_user_registered(event: UserRegistered) -> None:
    logger.info("User %s registered with id=%s", event.email, event.user_id)


async def on_order_created(event: OrderCreated) -> None:
    logger.info(
        "Order %s created with user_id=%s at %s",
        event.order_id,
        event.user_id,
        event.created_at,
    )
