from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base
from libs.mixins import IDMixin, TimeStampMixin

if TYPE_CHECKING:
    from app.domain.models.order_item import OrderItem


class OrderStatus(StrEnum):
    PENDING = "pending"
    RESERVED = "reserved"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(Base, IDMixin, TimeStampMixin):
    __tablename__ = "orders"
    __table_args__ = (Index("idx_orders_user_created", "user_id", "created_at"),)

    user_id: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
