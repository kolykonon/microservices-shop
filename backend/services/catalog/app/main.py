from fastapi import FastAPI

from app.api.v1.category import router as category_router
from app.api.v1.product import router as product_router

app: FastAPI = FastAPI()

app.include_router(router=category_router, prefix="/api/v1")
app.include_router(router=product_router, prefix="/api/v1")


@app.get(path="/health")
def health():
    return {"status": "ok"}
