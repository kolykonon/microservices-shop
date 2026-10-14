from typing import Annotated, override

from fastapi import Depends, HTTPException, status

from app.domain.models.category import Category
from app.domain.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.infra.repositories.category_repo import CategoryRepo, CategoryRepoDep
from app.infra.repositories.product_repo import ProductRepo, ProductRepoDep
from libs.base_service import BaseService


class CategoryService(
    BaseService[Category, CategoryCreate, CategoryUpdate, CategoryRead]
):
    read_schema = CategoryRead
    repo: CategoryRepo

    def __init__(self, repo: CategoryRepo, product_repo: ProductRepo):
        super().__init__(repo)
        self.product_repo = product_repo

    async def _ensure_name_free(self, name: str) -> None:
        if await self.repo.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with name {name} already exists",
            )

    @override
    async def create(self, data: CategoryCreate) -> CategoryRead:
        await self._ensure_name_free(data.name)
        return await super().create(data)

    @override
    async def update(self, id: int, data: CategoryUpdate) -> CategoryRead:
        category = await self._get_or_404(id)
        if data.name is not None and data.name != category.name:
            await self._ensure_name_free(data.name)
        category = await self.repo.update(category, data)
        return CategoryRead.model_validate(category)

    @override
    async def delete(self, id: int) -> None:
        category = await self._get_or_404(id)
        if await self.product_repo.get_list_by_category(id, limit=1):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with id={id} has products",
            )
        await self.repo.delete(category)


def get_category_service(
    repo: CategoryRepoDep,
    product_repo: ProductRepoDep,
) -> CategoryService:
    return CategoryService(repo, product_repo)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
