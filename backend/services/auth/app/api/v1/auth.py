from typing import Annotated

from app.domain.schemas.token import RefreshTokenRequest, TokenInfo
from app.domain.schemas.user import UserCreate, UserRead
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.domain.services.auth_service import AuthService, get_auth_service
from app.domain.services.token_store import (
    RefreshTokenStore,
    get_token_store,
)
from app.domain.services.user_service import UserService, get_user_service
from app.domain.utils.jwt import decode_token, encode_token
from app.infra.config import settings
from app.infra.repo import UserRepo, get_user_repo
from libs.deps import Auth
from libs.schemas.payload import PayloadInfo

auth = Auth(public_key=settings.jwt_public_key_path.read_text())

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    refreshUrl="/api/v1/auth/refresh",
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def __issue_tokens(
    user_id: str,
    store: Annotated[RefreshTokenStore, Depends(get_token_store)],
) -> TokenInfo:
    payload = {"sub": user_id}
    access = encode_token(payload, settings.jwt_access_token_type)
    refresh = encode_token(payload, settings.jwt_refresh_token_type)
    await store.save(user_id, refresh.jti, refresh.expires_at)
    return TokenInfo(access_token=access.token, refresh_token=refresh.token)


@router.post("/login", response_model=TokenInfo)
async def login(
    store: Annotated[RefreshTokenStore, Depends(get_token_store)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    email: str = Form(...),
    password: str = Form(...),
):
    user = await auth_service.authenticate_user(
        email=email,
        password=password,
    )
    return await __issue_tokens(str(user.id), store)


@router.post("/refresh", response_model=TokenInfo)
async def refresh(
    data: RefreshTokenRequest,
    store: Annotated[RefreshTokenStore, Depends(get_token_store)],
):
    try:
        payload = decode_token(
            data.refresh_token, expected_type=settings.jwt_refresh_token_type
        )
    except InvalidTokenError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if not await store.check(payload["jti"]):
        await store.revoke_all(payload["sub"])
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return await __issue_tokens(payload["sub"], store)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshTokenRequest,
    store: Annotated[RefreshTokenStore, Depends(get_token_store)],
):
    try:
        payload = decode_token(
            data.refresh_token,
            expected_type=settings.jwt_refresh_token_type,
        )
    except InvalidTokenError:
        return
    await store.revoke(payload["sub"], payload["jti"])


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    payload: Annotated[PayloadInfo, Depends(auth.current_user)],
    store: Annotated[RefreshTokenStore, Depends(get_token_store)],
):
    await store.revoke_all(payload.sub)


@router.get("/me", response_model=UserRead)
async def me(
    payload: Annotated[PayloadInfo, Depends(auth.current_user)],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
):
    user = await user_repo.get_user_by_id(int(payload.sub))
    return UserRead.model_validate(user, extra="ignore")


@router.post("/register", response_model=UserRead)
async def register(
    user_service: Annotated[UserService, Depends(get_user_service)], data: UserCreate
):
    return await user_service.create_user(data)
