from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product
from app.infra.db import get_session
from libs.base_repo import BaseRepo


class ProductRepo(BaseRepo[Product]):
    model = Product

    async def get_by_name(self, name: str) -> Product | None:
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_category(self, id: int) -> Product | None:
        query = (
            select(Product)
            .where(Product.id == id)
            .options(selectinload(Product.category))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_list_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Product]:
        query = (
            select(Product)
            .where(Product.category_id == category_id)
            .order_by(Product.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


def get_product_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProductRepo:
    return ProductRepo(session)


ProductRepoDep = Annotated[ProductRepo, Depends(get_product_repo)]
