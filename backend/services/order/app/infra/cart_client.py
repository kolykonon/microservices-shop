from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from app.domain.schemas.cart import CartRead


class CartClient:
    def __init__(self, client: AsyncClient) -> None:
        self.client: AsyncClient = client

    async def get_cart(self, token: str) -> CartRead:
        result = await self.client.get(
            url="/cart/",
            headers={"Authorization": f"Bearer {token}"},
        )
        result.raise_for_status()
        return CartRead.model_validate(result.json())


def get_cart_client(request: Request) -> CartClient:
    return CartClient(request.app.state.cart_http_client)


CartClientDep = Annotated[
    CartClient,
    Depends(dependency=get_cart_client),
]
