from datetime import UTC, datetime
from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Event(BaseModel):
    routing_key: ClassVar[str]

    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserRegistered(Event):
    routing_key: ClassVar[str] = "user.registered"

    user_id: int
    email: str


class OrderCreated(Event):
    routing_key: ClassVar[str] = "order.created"

    user_id: int
    order_id: int
    created_at: datetime
