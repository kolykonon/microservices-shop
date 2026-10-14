from fastapi import APIRouter, status

from app.api.deps import CurrentUser
from app.domain.cart_service import CartServiceDep
from app.domain.schemas.cart import CartItemAdd, CartItemUpdate, CartRead

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartRead)
async def get_cart(payload: CurrentUser, cart_service: CartServiceDep):
    return await cart_service.get_cart(
        int(payload.sub),
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(payload: CurrentUser, cart_service: CartServiceDep):
    await cart_service.clear_cart(int(payload.sub))


@router.post("/items", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_cart(
    data: CartItemAdd,
    payload: CurrentUser,
    cart_service: CartServiceDep,
):
    await cart_service.add_to_cart(int(payload.sub), data)


@router.patch("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def set_quantity(
    product_id: int,
    data: CartItemUpdate,
    payload: CurrentUser,
    cart_service: CartServiceDep,
):
    await cart_service.set_quantity(int(payload.sub), product_id, data.quantity)


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: int,
    payload: CurrentUser,
    cart_service: CartServiceDep,
):
    await cart_service.remove_from_cart(int(payload.sub), product_id)
