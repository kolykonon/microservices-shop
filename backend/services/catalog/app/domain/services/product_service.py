from collections.abc import Sequence
from typing import Annotated, override

from fastapi import Depends, HTTPException, status

from app.domain.models.product import Product
from app.domain.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductReadWithCategory,
    ProductUpdate,
)
from app.infra.repositories.category_repo import CategoryRepo, CategoryRepoDep
from app.infra.repositories.product_repo import ProductRepo, ProductRepoDep
from libs.base_service import BaseService


class ProductService(BaseService[Product, ProductCreate, ProductUpdate, ProductRead]):
    read_schema = ProductRead
    repo: ProductRepo

    def __init__(self, repo: ProductRepo, category_repo: CategoryRepo):
        super().__init__(repo)
        self.category_repo = category_repo

    async def _ensure_name_free(self, name: str) -> None:
        if await self.repo.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with name {name} already exists",
            )

    async def _ensure_category_exists(self, category_id: int) -> None:
        if await self.category_repo.get_by_id(category_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id={category_id} not found",
            )

    async def get_with_category(self, id: int) -> ProductReadWithCategory:
        product = await self.repo.get_by_id_with_category(id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id={id} not found",
            )
        return ProductReadWithCategory.model_validate(product)

    async def get_list_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ProductRead]:
        await self._ensure_category_exists(category_id)
        products = await self.repo.get_list_by_category(category_id, offset, limit)
        return [ProductRead.model_validate(product) for product in products]

    @override
    async def create(self, data: ProductCreate) -> ProductRead:
        await self._ensure_name_free(data.name)
        await self._ensure_category_exists(data.category_id)
        return await super().create(data)

    @override
    async def update(self, id: int, data: ProductUpdate) -> ProductRead:
        product = await self._get_or_404(id)
        if data.name is not None and data.name != product.name:
            await self._ensure_name_free(data.name)
        if data.category_id is not None:
            await self._ensure_category_exists(data.category_id)
        product = await self.repo.update(product, data)
        return ProductRead.model_validate(product)


def get_product_service(
    repo: ProductRepoDep,
    category_repo: CategoryRepoDep,
) -> ProductService:
    return ProductService(repo, category_repo)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
