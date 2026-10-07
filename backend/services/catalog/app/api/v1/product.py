from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser
from app.domain.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductReadWithCategory,
    ProductUpdate,
)
from app.domain.services.product_service import ProductServiceDep

router = APIRouter(prefix="/product", tags=["product"])


@router.get("/", response_model=list[ProductRead])
async def product_list(
    product_service: ProductServiceDep,
    category_id: int | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    if category_id is not None:
        return await product_service.get_list_by_category(category_id, offset, limit)
    return await product_service.get_list(offset, limit)


@router.get("/{product_id}", response_model=ProductReadWithCategory)
async def get_product(
    product_id: int,
    product_service: ProductServiceDep,
):
    return await product_service.get_with_category(product_id)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    product_service: ProductServiceDep,
    _: CurrentUser,
):
    return await product_service.create(data)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    product_service: ProductServiceDep,
    _: CurrentUser,
):
    return await product_service.update(product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    product_service: ProductServiceDep,
    _: CurrentUser,
):
    await product_service.delete(product_id)
