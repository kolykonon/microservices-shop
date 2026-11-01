from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class WarehouseCellCreate(BaseModel):
    """Schema for creating warehouse cell."""

    warehouse_id: UUID = Field(
        ...,
    )
    code: str = Field(
        max_length=100,
    )
    capacity: int = Field(
        ge=1,
    )


class WarehouseCellUpdate(BaseModel):
    """Schema for updating warehouse cell."""

    code: str | None = Field(
        default=None,
        max_length=100,
    )
    capacity: int | None = Field(
        default=None,
        ge=1,
    )
    sku: str | None = Field(
        default=None,
        max_length=255,
    )
    quantity: int | None = Field(
        default=None,
        ge=0,
    )

    @model_validator(mode="after")
    def quantity_fits_capacity(self):
        if (
            self.quantity is not None
            and self.capacity is not None
            and self.quantity > self.capacity
        ):
            raise ValueError("quantity cannot exceed capacity")
        return self


class WarehouseCellDelete(BaseModel):
    """Schema for deleting warehouse cell."""

    code: str


class WarehouseCellRead(BaseModel):
    """Schema for reading warehouse cell."""

    id: int
    warehouse_id: UUID
    code: str
    sku: str | None
    quantity: int
    capacity: int
    created_at: datetime
    updated_at: datetime


class WarehouseCreate(BaseModel):
    """Schema for creating warehouse."""

    name: str = Field(
        max_length=255,
    )
    adress: str = Field(
        max_length=300,
    )


class WarehouseRead(BaseModel):
    id: UUID
    name: str
    adress: str
    is_active: bool
    cells: list[WarehouseCellRead] | list[None] = Field(default_factory=list[None])
