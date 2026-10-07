from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.infra.config import settings

engine = create_async_engine(settings.postgres_url)

session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase): ...


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


SessionDep = Annotated[
    AsyncIterator[AsyncSession],
    Depends(get_session),
]
