from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.stock_receipt_item import StockReceiptItem
    from app.models.supplier import Supplier
    from app.models.user import User


class StockReceipt(BaseModel):
    __tablename__ = "stock_receipts"

    receipt_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
    )
    received_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    supplier: Mapped["Supplier | None"] = relationship(back_populates="stock_receipts")
    receiver: Mapped["User"] = relationship(back_populates="stock_receipts")
    items: Mapped[list["StockReceiptItem"]] = relationship(back_populates="receipt")
