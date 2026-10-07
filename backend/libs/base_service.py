from collections.abc import Sequence
from typing import Any, ClassVar

from fastapi import HTTPException, status
from pydantic import BaseModel

from libs.base_repo import BaseRepo


class BaseService[
ModelT,
CreateT: BaseModel,
UpdateT: BaseModel,
ReadT: BaseModel,
]:
    read_schema = type[ReadT]

    def __init__(self, repo: BaseRepo[ModelT]):
        self.repo = repo

    async def _get_or_404(self, id: int) -> ModelT:
        obj = await self.repo.get_by_id(id)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.repo.model.__name__} with id={id} not found",
            )
        return obj

    async def get(self, id: int) -> ReadT:
        obj = await self._get_or_404(id)
        return self.read_schema.model_validate(obj)

    async def get_list(
            self,
            offset: int = 0,
            limit: int = 100,
    ) -> Sequence[ReadT]:
        objs = await self.repo.get_list(offset, limit)
        return [self.read_schema.model_validate(obj) for obj in objs]

    async def create(self, data: CreateT) -> ReadT:
        obj = await self.repo.create(data)
        return self.read_schema.model_validate(obj)

    async def update(self, id: int, data: UpdateT) -> ReadT:
        obj = await self._get_or_404(id)
        obj = await self.repo.update(obj, data)
        return self.read_schema.model_validate(obj)

    async def delete(self, id: int) -> None:
        obj = await self._get_or_404(id)
        await self.repo.delete(obj)

