from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base
from libs.mixins import IDMixin, TimeStampMixin

if TYPE_CHECKING:
    from app.domain.models.category import Category


class Product(Base, IDMixin, TimeStampMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        unique=True,
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    category: Mapped["Category"] = relationship(back_populates="products")
