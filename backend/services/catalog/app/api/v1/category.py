from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser
from app.domain.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.domain.services.category_service import CategoryServiceDep

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/", response_model=list[CategoryRead])
async def category_list(
        category_service: CategoryServiceDep,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return await category_service.get_list(offset, limit)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
        category_id: int,
        category_service: CategoryServiceDep,
):
    return await category_service.get(category_id)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
        data: CategoryCreate,
        category_service: CategoryServiceDep,
        _: CurrentUser,
):
    return await category_service.create(data)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
        category_id: int,
        data: CategoryUpdate,
        category_service: CategoryServiceDep,
        _: CurrentUser,
):
    return await category_service.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        category_service: CategoryServiceDep,
        _: CurrentUser,
):
    await category_service.delete(category_id)
