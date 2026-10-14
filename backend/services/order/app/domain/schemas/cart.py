from decimal import Decimal

from pydantic import BaseModel


class ProductRead(BaseModel):
    id: int
    name: str
    price: Decimal


class CartItemRead(BaseModel):
    product: ProductRead
    quantity: int


class CartRead(BaseModel):
    items: list[CartItemRead]
    total_quantity: int
    total_price: Decimal
