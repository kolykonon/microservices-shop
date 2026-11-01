from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from libs.mixins import IDMixin, TimeStampMixin


class WarehouseCell(Base, IDMixin, TimeStampMixin):
    """Class that represents warehouse cell, that stores products."""

    __tablename__ = "warehouse_cells"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "code"),
    )  # cell code is unique inside warehouse

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE")
    )
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    sku: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )  # foreign key on products (if null, cell is empty)
    quantity: Mapped[int | None] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="cells",
    )


class Warehouse(Base, TimeStampMixin):
    """Warehouse class. Contains list of cells that stores products."""

    __tablename__ = "warehouses"

    __table_args__ = (
        UniqueConstraint("name", name="uq_warehouses_name"),
        UniqueConstraint("address", name="uq_warehouses_address"),
    )  # name and adress are unique, name is used in service to define domain exception

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
    cells: Mapped[list[WarehouseCell]] = relationship(
        back_populates="warehouse",
        cascade="all, delete-orphan",  # if we delete warehouse, cells deletes too
    )
