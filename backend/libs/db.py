from collections.abc import AsyncIterator, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def make_dependency(db_url: str) -> Callable:
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    return get_session
