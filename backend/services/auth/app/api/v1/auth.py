from typing import Annotated

from app.domain.schemas.token import TokenInfo
from app.domain.schemas.user import UserCreate, UserRead
from app.domain.services.auth_service import AuthService, get_auth_service
from app.domain.services.user_service import UserService, get_user_service
from app.domain.utils.jwt import encode_token
from app.infra.config import settings
from app.infra.repo import UserRepo, get_user_repo
from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordBearer

from libs.deps import Auth
from libs.schemas.payload import PayloadInfo

auth = Auth(public_key=settings.jwt_public_key_path.read_text())

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenInfo)
async def login(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    email: str = Form(...),
    password: str = Form(...),
):
    user = await auth_service.authenticate_user(
        email=email,
        password=password,
    )
    payload = {"sub": str(user.id)}
    access_token = encode_token(
        payload=payload,
        token_type=settings.jwt_access_token_type,
    )
    refresh_token = encode_token(
        payload=payload,
        token_type=settings.jwt_refresh_token_type,
    )
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


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

