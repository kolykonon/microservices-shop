from fastapi import APIRouter

from app.schemas.warehouse import WarehouseCreate, WarehouseRead

from ..deps import WarehouseServiceDep

router = APIRouter(prefix="/warehouse", tags=["warehouses"])


@router.post("/", response_model=WarehouseRead)
async def create_warehouse(data: WarehouseCreate, service: WarehouseServiceDep):
    return await service.create_warehouse(data)
