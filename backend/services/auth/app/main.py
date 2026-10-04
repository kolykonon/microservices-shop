from app.api.v1.auth import router as auth_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
