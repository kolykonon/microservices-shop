from typing import Annotated

from fastapi import Depends

from app.domain.exceptions import AlreadyExistsError, NotFoundError
from app.domain.schemas.user import (
    UserCreate,
    UserCreateDB,
    UserRead,
    UserUpdate,
    UserUpdateDB,
)
from app.domain.utils.security import hash_password
from app.infra.rabbit import RabbitDep
from app.infra.repo import UserRepoDep
from libs.events import UserRegistered


class UserService:
    def __init__(self, repo: UserRepoDep, rabbit: RabbitDep):
        self.repo = repo
        self.rabbit = rabbit

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

        new_user = await self.repo.create_user(user_db_schema)
        await self.rabbit.publish(
            UserRegistered(user_id=new_user.id, email=new_user.email)
        )
        return UserRead.model_validate(new_user)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserRead:
        existed = await self.repo.get_user_by_id(user_id)
        if not existed:
            raise NotFoundError(f"User with id={user_id} not found")
        if data.password:
            data.password = hash_password(data.password)
        user_db_schema = UserUpdateDB(email=data.email, hashed_password=data.password)
        await self.repo.update_user(existed, user_db_schema)
        return UserRead.model_validate(existed)

    async def delete_user(self, user_id: int) -> None:
        existed = await self.repo.get_user_by_id(user_id)
        if not existed:
            raise NotFoundError(f"User with id={user_id} not found")
        await self.repo.delete_user(existed)


def get_user_service(repo: UserRepoDep, rabbit: RabbitDep) -> UserService:
    return UserService(repo, rabbit)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
