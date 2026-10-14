from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base
from libs.mixins import IDMixin, TimeStampMixin

if TYPE_CHECKING:
    from app.domain.models.product import Product


class Category(Base, IDMixin, TimeStampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    products: Mapped[list["Product"]] = relationship(back_populates="category")
