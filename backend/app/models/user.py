from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.inventory_transaction import InventoryTransaction
    from app.models.product_note import ProductNote
    from app.models.role import Role
    from app.models.sale import Sale
    from app.models.stock_receipt import StockReceipt


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )

    role: Mapped["Role | None"] = relationship(back_populates="users")
    product_notes: Mapped[list["ProductNote"]] = relationship(back_populates="author")
    stock_receipts: Mapped[list["StockReceipt"]] = relationship(back_populates="receiver")
    sales: Mapped[list["Sale"]] = relationship(back_populates="cashier")
    inventory_transactions: Mapped[list["InventoryTransaction"]] = relationship(
        back_populates="creator"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
