from fastapi import APIRouter, Form, status
from fastapi.security import OAuth2PasswordBearer

from app.api.deps import CurrentUserDep
from app.domain.schemas.token import RefreshTokenRequest, TokenInfo
from app.domain.schemas.user import UserCreate, UserRead
from app.domain.services.auth_service import (
    AuthServiceDep,
)
from app.domain.services.user_service import (
    UserServiceDep,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login", refreshUrl="/api/v1/auth/refresh"
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenInfo)
async def login(
    auth_service: AuthServiceDep, email: str = Form(...), password: str = Form(...)
):
    return await auth_service.authenticate_user(email=email, password=password)


@router.post("/refresh", response_model=TokenInfo)
async def refresh(data: RefreshTokenRequest, auth_service: AuthServiceDep):
    return await auth_service.refresh_token(data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshTokenRequest, auth_service: AuthServiceDep):
    return await auth_service.logout(data)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    payload: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    await auth_service.logout_all(payload)


@router.get("/me", response_model=UserRead)
async def me(
    payload: CurrentUserDep,
    auth_service: AuthServiceDep,
):
    return await auth_service.get_me(payload)


@router.post("/register", response_model=UserRead)
async def register(user_service: UserServiceDep, data: UserCreate):
    return await user_service.create_user(data)
