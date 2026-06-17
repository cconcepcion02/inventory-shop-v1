from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product


class ProductCrossReference(BaseModel):
    __tablename__ = "product_cross_references"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "equivalent_product_id",
            name="uq_product_cross_reference_pair",
        ),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    equivalent_product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    product: Mapped["Product"] = relationship(
        back_populates="cross_references",
        foreign_keys=[product_id],
    )
    equivalent_product: Mapped["Product"] = relationship(
        back_populates="equivalent_of",
        foreign_keys=[equivalent_product_id],
    )
