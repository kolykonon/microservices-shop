from app.infra.db import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from libs.mixins import IDMixin, TimeStampMixin


class UserModel(Base, IDMixin, TimeStampMixin):
    """ORM модель пользователя"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
