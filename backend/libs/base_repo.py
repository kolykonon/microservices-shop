from collections.abc import Sequence
from typing import Any, ClassVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo[ModelT]:
    model: ClassVar[type[Any]]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def get_list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelT]:
        query = select(self.model).order_by(self.model.id).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, data: BaseModel) -> ModelT:
        obj = self.model(**data.model_dump())
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelT, data: BaseModel) -> ModelT:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.commit()
