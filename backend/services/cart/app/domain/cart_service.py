from decimal import Decimal
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.domain.schemas.cart import CartItem, CartItemAdd, CartItemRead, CartRead
from app.infra.cart_repo import CartRepo, CartRepoDep
from app.infra.catalog_client import CatalogClient, CatalogClientDep


class CartService:
    def __init__(
        self,
        catalog_client: CatalogClient,
        cart_repo: CartRepo,
    ) -> None:
        self.catalog_client: CatalogClient = catalog_client
        self.cart_repo: CartRepo = cart_repo

    async def get_cart(self, user_id: int) -> CartRead:
        cart = await self.cart_repo.get_cart(user_id)
        if not cart.items:
            return CartRead(total_quantity=0, total_price=Decimal(0), items=[])

        quantities = {item.product_id: item.quantity for item in cart.items}
        products = await self.catalog_client.get_cart_product_list(list(quantities))
        items = [
            CartItemRead(product=product, quantity=quantities[product.id])
            for product in products
        ]
        return CartRead(
            items=items,
            total_quantity=sum(item.quantity for item in items),
            total_price=sum(
                (item.product.price * item.quantity for item in items),
                Decimal(0),
            ),
        )

    async def add_to_cart(self, user_id: int, data: CartItemAdd) -> None:
        await self.catalog_client.get_product_by_id(data.product_id)
        await self.cart_repo.add_to_cart(user_id, CartItem(**data.model_dump()))

    async def remove_from_cart(self, user_id: int, product_id: int) -> None:
        if not await self.cart_repo.remove_from_cart(user_id, product_id):
            self._raise_not_in_cart(product_id)

    async def set_quantity(self, user_id: int, product_id: int, quantity: int) -> None:
        if not await self.cart_repo.set_quantity(user_id, product_id, quantity):
            self._raise_not_in_cart(product_id)

    async def clear_cart(self, user_id: int) -> None:
        await self.cart_repo.clear_cart(user_id)

    @staticmethod
    def _raise_not_in_cart(product_id: int) -> None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not in cart",
        )


def get_cart_service(
    catalog_client: CatalogClientDep, cart_repo: CartRepoDep
) -> CartService:
    return CartService(catalog_client, cart_repo)


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]
