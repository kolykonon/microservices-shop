from fastapi import APIRouter, status

from app.api.deps import CurrentUser, Token
from app.domain.schemas.order import OrderRead
from app.domain.services.order_service import OrderServiceDep

router = APIRouter(prefix="/orders", tags=["order"])


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CurrentUser,
    token: Token,
    order_service: OrderServiceDep,
):
    return await order_service.create_from_cart(int(payload.sub), token.credentials)
