import logging
from collections.abc import Awaitable, Callable
from typing import Self

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractRobustConnection

from libs.events import Event

EXCHANGE_NAME = "shop.events"

logger = logging.getLogger(__name__)


async def declare_exchange(channel: AbstractChannel) -> AbstractExchange:
    return await channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )


class Rabbit:
    def __init__(
        self,
        connection: AbstractRobustConnection,
        channel: AbstractChannel,
        exchange: AbstractExchange,
    ):
        self.connection = connection
        self.channel = channel
        self.exchange = exchange

    @classmethod
    async def connect(cls, url: str) -> Self:
        connection = await aio_pika.connect_robust(url)
        channel = await connection.channel()
        exchange = await declare_exchange(channel)
        return cls(connection, channel, exchange)

    async def close(self) -> None:
        await self.connection.close()

    async def publish(self, event: Event) -> None:
        message = aio_pika.Message(
            body=event.model_dump_json().encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            message_id=str(event.event_id),
            type=event.routing_key,
        )
        await self.exchange.publish(message, routing_key=event.routing_key)

    async def consume[E: Event](
        self,
        queue_name: str,
        event_type: type[E],
        handler: Callable[[E], Awaitable[None]],
        prefetch_count: int = 10,
        max_retries: int = 3,
        retry_delay_ms: int = 5000,
    ) -> None:
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=prefetch_count)
        exchange = await declare_exchange(channel)
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=event_type.routing_key)

        retry_queue_name = f"{queue_name}.retry"
        dlq_name = f"{queue_name}.dlq"
        await channel.declare_queue(
            retry_queue_name,
            durable=True,
            arguments={
                "x-message-ttl": retry_delay_ms,
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": queue_name,
            },
        )
        await channel.declare_queue(dlq_name, durable=True)

        async with queue.iterator() as messages:
            async for message in messages:
                async with message.process(requeue=False):
                    try:
                        await handler(event_type.model_validate_json(message.body))
                    except Exception:
                        retries = int((message.headers or {}).get("x-retries", 0))
                        target = retry_queue_name if retries < max_retries else dlq_name
                        logger.exception(
                            "Failed to process message %s, attempt %s, sending to %s",
                            message.message_id,
                            retries + 1,
                            target,
                        )
                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=message.body,
                                content_type=message.content_type,
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                message_id=message.message_id,
                                type=message.type,
                                headers={
                                    **(message.headers or {}),
                                    "x-retries": retries + 1,
                                },
                            ),
                            routing_key=target,
                        )
