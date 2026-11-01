from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate


class WarehouseRepo:
    """Repository for working with warehouses table."""

    def __init__(
        self,
        session: AsyncSession,
        model: type[Warehouse],
    ) -> None:
        self.session = session
        self.model = model

    async def create_warehouse(self, data: WarehouseCreate) -> Warehouse:
        """Method for creating new warehouse in database.

        Params:
            data: pydantic schema for creating warehouse.

        """
        stmt = text(
            """
            INSERT INTO warehouses (name, adress)
            VALUES (:name, :adress)
            """
        )  # raw sql is used only for educational purposes
        result = await self.session.execute(
            stmt,
            params={"name": data.name, "adress": data.adress},
        )
        await self.session.commit()
        return result.scalar_one()
