from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.sale_item import SaleItem
    from app.models.user import User


class Sale(BaseModel):
    __tablename__ = "sales"

    sale_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    cashier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_tendered: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    change_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    cashier: Mapped["User"] = relationship(back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale")
