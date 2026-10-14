from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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


def get_order_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrderRepo:
    return OrderRepo(session)


OrderRepoDep = Annotated[OrderRepo, Depends(get_order_repo)]
