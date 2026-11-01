from typing import Annotated

from fastapi import Depends

from app.core.db import SessionDep
from app.models.warehouse import Warehouse
from app.repositories.warehouse_repo import WarehouseRepo
from app.services.warehouse_service import WarehouseService


def get_warehouse_repo(
    session: SessionDep,
    model: type[Warehouse],
) -> WarehouseRepo:
    return WarehouseRepo(session, model)


WarehouseRepoDep = Annotated[WarehouseRepo, Depends(get_warehouse_repo)]


def get_warehouse_service(
    repo: WarehouseRepoDep,
) -> WarehouseService:
    return WarehouseService(repo)


WarehouseServiceDep = Annotated[WarehouseService, Depends(get_warehouse_service)]
