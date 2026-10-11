from typing import Annotated

from fastapi import Depends
from jwt import InvalidTokenError

from app.domain.exceptions import InvalidCredentialsError, InvalidRefreshTokenError
from app.domain.schemas.token import RefreshTokenRequest, TokenInfo
from app.domain.schemas.user import UserRead
from app.domain.services.token_store import TokenStoreDep
from app.domain.utils.jwt_token import decode_token, encode_token
from app.domain.utils.security import dummy_hash, verify_password
from app.infra.config import settings
from app.infra.repo import UserRepoDep
from libs.schemas.payload import PayloadInfo


class AuthService:
    def __init__(self, user_repo: UserRepoDep, store: TokenStoreDep):
        self.user_repo = user_repo
        self.store = store

    async def __issue_tokens(self, user_id: str) -> TokenInfo:
        payload = {"sub": user_id}
        access = encode_token(payload, settings.jwt_access_token_type)
        refresh = encode_token(payload, settings.jwt_refresh_token_type)
        await self.store.save(user_id, refresh.jti, refresh.expires_at)
        return TokenInfo(access_token=access.token, refresh_token=refresh.token)

    async def authenticate_user(self, email: str, password: str) -> TokenInfo:
        existed = await self.user_repo.get_user_by_email(email)
        if not existed:
            verify_password(password, dummy_hash)
            raise InvalidCredentialsError("Wrong email or password")

        if not verify_password(password, existed.hashed_password):
            raise InvalidCredentialsError("Wrong email or password")

        return await self.__issue_tokens(str(existed.id))

    async def refresh_token(self, data: RefreshTokenRequest) -> TokenInfo:
        try:
            payload = decode_token(
                data.refresh_token, expected_type=settings.jwt_refresh_token_type
            )
        except InvalidTokenError:
            raise InvalidRefreshTokenError("Invalid refresh token")
        if not await self.store.consume(payload["jti"]):
            await self.store.revoke_all(payload["sub"])
            raise InvalidRefreshTokenError("Invalid refresh token")
        return await self.__issue_tokens(payload["sub"])

    async def logout(self, data: RefreshTokenRequest) -> None:
        try:
            payload = decode_token(
                data.refresh_token,
                expected_type=settings.jwt_refresh_token_type,
            )
        except InvalidTokenError:
            return
        await self.store.revoke(payload["sub"], payload["jti"])

    async def logout_all(self, payload: PayloadInfo) -> None:
        await self.store.revoke_all(payload.sub)

    async def get_me(self, payload: PayloadInfo) -> UserRead:
        user = await self.user_repo.get_user_by_id(int(payload.sub))
        return UserRead.model_validate(user, extra="ignore")


def get_auth_service(user_repo: UserRepoDep, token_store: TokenStoreDep) -> AuthService:
    return AuthService(user_repo, token_store)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
