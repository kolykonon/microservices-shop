from fastapi import APIRouter

from app.api.v1.cart import router as cart_router

router = APIRouter(prefix="/api/v1", tags=["api/v1"])

router.include_router(cart_router, tags=["cart"])
