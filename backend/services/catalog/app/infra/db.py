from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.infra.config import settings
from libs.db import make_dependency


class Base(DeclarativeBase): ...


get_session = make_dependency(settings.postgres_url)

SessionDep = Annotated[AsyncSession, Depends(get_session)]
