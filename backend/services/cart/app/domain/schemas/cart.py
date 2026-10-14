from decimal import Decimal

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class Cart(BaseModel):
    items: list[CartItem]


class CartItemAdd(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=99)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, le=99)


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
