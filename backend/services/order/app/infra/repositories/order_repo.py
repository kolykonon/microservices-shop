from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, override

from fastapi import Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import selectinload

from app.domain.models.order import Order
from app.infra.db import get_session
from libs.base_repo import BaseRepo


class OrderRepo(BaseRepo[Order]):
    model = Order

    async def create_order(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order, ["created_at", "updated_at", "items"])
        return order

    @override
    async def get_list(
        self, offset: int | None = None, limit: int | None = None
    ) -> Sequence[Order]:
        query = text("""
            SELECT *
            FROM orders o
            ORDER BY o.created_at, o.id
            LIMIT :limit
            OFFSET :offset
            """)
        stmt = select(Order).from_statement(query).options(selectinload(Order.items))
        result = await self.session.execute(stmt, {"limit": limit, "offset": offset})
        return result.scalars().all()

    async def get_user_orders_between_dates(
        self, user_id: int, date_start: datetime, date_end: datetime
    ) -> Sequence[Order]:
        query = text("""
            SELECT *
            FROM orders o
            WHERE o.user_id = :user_id AND
            o.created_at BETWEEN :date_start AND :date_end
            ORDER BY o.created_at
            """)
        stmt = select(Order).from_statement(query).options(selectinload(Order.items))
        result = await self.session.execute(
            stmt, {"date_start": date_start, "date_end": date_end, "user_id": user_id}
        )
        return result.scalars().all()


def get_order_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrderRepo:
    return OrderRepo(session)


OrderRepoDep = Annotated[OrderRepo, Depends(get_order_repo)]
