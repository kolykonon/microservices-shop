from collections.abc import AsyncIterator
from typing import Annotated

from app.infra.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from libs.db import make_dependency


class Base(DeclarativeBase):
    pass


get_session = make_dependency(settings.postgres_url)

SessionDep = Annotated[AsyncIterator[AsyncSession], get_session]
