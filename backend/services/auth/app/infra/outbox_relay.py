import asyncio
import logging

from app.infra.db import session_factory
from app.infra.outbox_repo import OutboxRepo
from libs.events import Event, UserRegistered
from libs.rabbit import Rabbit

logger = logging.getLogger(__name__)

EVENTS: dict[str, type[Event]] = {
    UserRegistered.routing_key: UserRegistered,
}


async def publish_batch(rabbit: Rabbit, batch_size: int) -> int:
    async with session_factory() as session:
        repo = OutboxRepo(session)
        messages = await repo.get_unpublished(batch_size)
        for message in messages:
            event = EVENTS[message.event_type].model_validate(message.payload)
            await rabbit.publish(event)
            repo.mark_published(message)
        await session.commit()
        return len(messages)


async def run_outbox_relay(
    rabbit: Rabbit, interval: float = 1.0, batch_size: int = 100
) -> None:
    while True:
        try:
            published = await publish_batch(rabbit, batch_size)
        except Exception:
            logger.exception("Outbox relay iteration failed")
            published = 0
        if published < batch_size:
            await asyncio.sleep(interval)
