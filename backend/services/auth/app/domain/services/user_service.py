from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import AlreadyExistsError, NotFoundError
from app.domain.schemas.user import (
    UserCreate,
    UserCreateDB,
    UserRead,
    UserUpdate,
    UserUpdateDB,
)
from app.domain.services.token_store import RefreshTokenStore, TokenStoreDep
from app.domain.utils.security import hash_password
from app.infra.outbox_repo import OutboxRepo, OutboxRepoDep
from app.infra.user_repo import UserRepoDep
from libs.events import UserRegistered


class UserService:
    def __init__(
        self,
        repo: UserRepoDep,
        outbox: OutboxRepo,
        token_store: RefreshTokenStore,
    ):
        self.repo = repo
        self.outbox = outbox
        self.token_store = token_store

    async def get_user_by_email(self, email: str) -> UserRead | None:
        user = await self.repo.get_user_by_email(email)
        if not user:
            return None
        return UserRead.model_validate(user)

    async def create_user(self, data: UserCreate) -> UserRead:
        existed_user = await self.get_user_by_email(data.email)

        if existed_user:
            raise AlreadyExistsError(f"User with email {data.email} already exists")

        hashed_password = hash_password(data.password.get_secret_value())
        user_db_schema = UserCreateDB(email=data.email, hashed_password=hashed_password)

        try:
            new_user = await self.repo.create_user(user_db_schema)
        except IntegrityError as e:
            await self.repo.session.rollback()
            raise AlreadyExistsError(
                f"User with email {data.email} already exists"
            ) from e

        self.outbox.add(UserRegistered(user_id=new_user.id, email=new_user.email))
        await self.repo.session.commit()
        await self.repo.session.refresh(new_user)
        return UserRead.model_validate(new_user)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserRead:
        existed = await self.repo.get_user_by_id(user_id)
        if not existed:
            raise NotFoundError(f"User with id={user_id} not found")

        if data.password:
            data.password = hash_password(data.password)
            await self.token_store.revoke_all(str(user_id))

        user_db_schema = UserUpdateDB(**data.model_dump(exclude_unset=True))
        await self.repo.update_user(existed, user_db_schema)
        return UserRead.model_validate(existed)

    async def delete_user(self, user_id: int) -> None:
        existed = await self.repo.get_user_by_id(user_id)
        if not existed:
            raise NotFoundError(f"User with id={user_id} not found")
        await self.repo.delete_user(existed)
        await self.token_store.revoke_all(str(user_id))


def get_user_service(
    repo: UserRepoDep,
    outbox: OutboxRepoDep,
    token_store: TokenStoreDep,
) -> UserService:
    return UserService(repo, outbox, token_store)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
