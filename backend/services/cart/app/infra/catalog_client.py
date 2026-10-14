from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient

from app.domain.schemas.cart import ProductRead


class CatalogClient:
    def __init__(
        self,
        client: AsyncClient,
    ) -> None:
        self.client: AsyncClient = client

    async def get_cart_product_list(self, ids: list[int]) -> list[ProductRead]:
        result = await self.client.get(
            url="/products/products-by-ids",
            params={"ids": ids},
        )
        result.raise_for_status()
        result = result.json()
        return [ProductRead.model_validate(item) for item in result]

    async def get_product_by_id(self, product_id: int) -> ProductRead:
        result = await self.client.get(url=f"/products/{product_id}")
        result.raise_for_status()
        result = result.json()
        return ProductRead.model_validate(result)


def get_catalog_client(request: Request) -> CatalogClient:
    return CatalogClient(request.app.state.catalog_http_client)


CatalogClientDep = Annotated[
    CatalogClient,
    Depends(dependency=get_catalog_client),
]
