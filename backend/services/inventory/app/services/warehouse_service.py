import logging

from sqlalchemy.exc import IntegrityError

from app.repositories.warehouse_repo import WarehouseRepo
from app.schemas.warehouse import WarehouseCreate, WarehouseRead


class WarehouseDomainException(Exception):
    """Basic exception for warehouse domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class WarehouseNameAlreadyExists(WarehouseDomainException):
    """Exception that throws when warehouse with such name already exists."""

    pass


class WarehouseAdressAlreadyExists(WarehouseDomainException):
    """Exception that throws when warehouse with such adress already exists."""

    pass


class WarehouseService:
    """Class that implements warehouses business logic."""

    def __init__(
        self,
        repo: WarehouseRepo,
    ) -> None:
        self.repo = repo
        self.logger = logging.getLogger(self.__class__.__name__)
        self.redis = ...

    async def create_warehouse(
        self,
        data: WarehouseCreate,
    ) -> WarehouseRead:
        """Method for creating warehouse in database."""

        self.logger.info(
            "Started creating warehouse with name=%s, adress=%s",
            data.name,
            data.adress,
        )
        try:
            result = await self.repo.create_warehouse(data)
            self.logger.info(
                "Warehouse with name=%s,adress=%s created successfully",
                data.name,
                data.adress,
            )
            return WarehouseRead.model_validate(result)
        except IntegrityError as e:
            self.logger.info(
                "Failed to create warehouse with name=%s,"
                "adress=%s due to IntegrityEror %e",
                data.name,
                data.adress,
                e.orig,
            )
            constraint = getattr(
                getattr(getattr(e, "orig", None), "diag", None),
                "constraint_name",
                None,
            )  # get constraint name from sqlalchemy error
            match constraint:  # mapping constraint to proper domain exception
                case "uq_warehouses_name":
                    raise WarehouseNameAlreadyExists(
                        f"Warehouse with name={data.name} already exists"
                    ) from e
                case "uq_warehouses_adress":
                    raise WarehouseAdressAlreadyExists(
                        f"Warehouse with adress={data.adress} already exists"
                    ) from e
                case _:
                    raise WarehouseDomainException(
                        "Error while creating new warehouse"
                    ) from e
