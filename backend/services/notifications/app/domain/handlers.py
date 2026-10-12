import logging

from libs.events import UserRegistered

logger = logging.getLogger(__name__)


async def on_user_registered(event: UserRegistered) -> None:
    logger.info("User %s registered with id=%s", event.email, event.user_id)
