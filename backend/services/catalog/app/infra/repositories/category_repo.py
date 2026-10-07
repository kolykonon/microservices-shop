from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.category import Category
from app.infra.db import get_session
from libs.base_repo import BaseRepo


class CategoryRepo(BaseRepo[Category]):
    model = Category

    async def get_by_name(self, name: str) -> Category | None:
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


def get_category_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CategoryRepo:
    return CategoryRepo(session)


CategoryRepoDep = Annotated[CategoryRepo, Depends(get_category_repo)]
