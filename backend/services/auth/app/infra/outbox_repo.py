from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.outbox_message import OutboxMessage
from app.infra.db import SessionDep
from libs.events import Event


class OutboxRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, event: Event) -> OutboxMessage:
        message = OutboxMessage(
            event_type=event.routing_key,
            payload=event.model_dump(mode="json"),
        )
        self.session.add(message)
        return message

    async def get_unpublished(self, limit: int) -> Sequence[OutboxMessage]:
        query = (
            select(OutboxMessage)
            .where(OutboxMessage.published_at.is_(None))
            .order_by(OutboxMessage.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    def mark_published(self, message: OutboxMessage) -> None:
        message.published_at = datetime.now(UTC)


def get_outbox_repo(session: SessionDep) -> OutboxRepo:
    return OutboxRepo(session)


OutboxRepoDep = Annotated[OutboxRepo, Depends(get_outbox_repo)]
