from typing import Annotated

from app.domain.models.user import UserModel
from fastapi import Depends, HTTPException, status

from app.domain.utils.security import dummy_hash, verify_password
from app.infra.repo import UserRepo, get_user_repo


class AuthService:
    def __init__(
        self,
        user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    ):
        self.user_repo = user_repo

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> UserModel:
        wrong_credentials_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong email or password",
        )
        existed = await self.user_repo.get_user_by_email(email)
        if not existed:
            verify_password(password, dummy_hash)
            raise wrong_credentials_exception
        if not verify_password(password, existed.hashed_password):
            raise wrong_credentials_exception
        return existed


def get_auth_service(
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
) -> AuthService:
    return AuthService(user_repo)
