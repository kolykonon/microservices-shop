from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.warehouse_service import (
    WarehouseAdressAlreadyExists,
    WarehouseDomainException,
    WarehouseNameAlreadyExists,
)

STATUS_CODES = {
    WarehouseNameAlreadyExists: status.HTTP_409_CONFLICT,
    WarehouseAdressAlreadyExists: status.HTTP_409_CONFLICT,
}


async def domain_error_handler(
    request: Request, exc: WarehouseDomainException
) -> JSONResponse:
    status_code = STATUS_CODES.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


async def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(WarehouseDomainException, domain_error_handler)
