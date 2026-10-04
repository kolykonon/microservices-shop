from typing import Annotated

from app.domain.models.user import UserModel
from app.domain.schemas.user import UserCreateDB, UserUpdateDB
from app.infra.db import get_session
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo:
    def __init__(
        self,
        session: Annotated[
            AsyncSession,
            Depends(get_session),
        ],
    ):
        self.session = session

    async def get_user_by_email(
        self,
        email: str,
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        id: int,
    ) -> UserModel | None:
        query = select(UserModel).where(UserModel.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        data: UserCreateDB,
    ) -> UserModel:
        new_user = UserModel(**data.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.flush()
        return new_user

    async def update_user(
        self,
        user: UserModel,
        data: UserUpdateDB,
    ) -> UserModel:
        for key, value in data.model_dump(exclude_unset=True):
            setattr(user, key, value)
        await self.session.commit()
        await self.session.flush()
        return user

    async def delete_user(self, user: UserModel) -> None:
        await self.session.delete(user)
        await self.session.commit()


def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepo:
    return UserRepo(session)
