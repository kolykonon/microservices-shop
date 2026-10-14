from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.domain.models.order import Order
from app.domain.models.order_item import OrderItem
from app.domain.schemas.order import OrderRead
from app.infra.cart_client import CartClient, CartClientDep
from app.infra.rabbit import RabbitDep
from app.infra.repositories.order_repo import OrderRepo, OrderRepoDep
from libs.events import OrderCreated


class OrderService:
    def __init__(
        self, repo: OrderRepo, cart_client: CartClient, rabbit: RabbitDep
    ) -> None:
        self.repo: OrderRepo = repo
        self.cart_client: CartClient = cart_client
        self.rabbit: RabbitDep = rabbit

    async def create_from_cart(self, user_id: int, token: str) -> OrderRead:
        cart = await self.cart_client.get_cart(token)
        if not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )
        order = Order(
            user_id=user_id,
            total_price=cart.total_price,
            items=[
                OrderItem(
                    product_id=item.product.id,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                for item in cart.items
            ],
        )
        order = await self.repo.create_order(order)
        await self.rabbit.publish(
            OrderCreated(
                user_id=user_id,
                order_id=order.id,
                created_at=order.created_at,
            )
        )
        return OrderRead.model_validate(order)


def get_order_service(
    repo: OrderRepoDep,
    cart_client: CartClientDep,
    rabbit: RabbitDep,
) -> OrderService:
    return OrderService(repo, cart_client, rabbit)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]