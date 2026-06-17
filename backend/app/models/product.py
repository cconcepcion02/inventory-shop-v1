from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.category import Category
    from app.models.inventory_transaction import InventoryTransaction
    from app.models.product_cross_reference import ProductCrossReference
    from app.models.product_image import ProductImage
    from app.models.product_note import ProductNote
    from app.models.sale_item import SaleItem
    from app.models.stock_receipt_item import StockReceiptItem
    from app.models.supplier import Supplier


class Product(BaseModel):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
    )
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reorder_level: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    category: Mapped["Category | None"] = relationship(back_populates="products")
    brand: Mapped["Brand | None"] = relationship(back_populates="products")
    supplier: Mapped["Supplier | None"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="save-update, merge",
        order_by="ProductImage.sort_order",
    )
    notes: Mapped[list["ProductNote"]] = relationship(back_populates="product")
    cross_references: Mapped[list["ProductCrossReference"]] = relationship(
        foreign_keys="ProductCrossReference.product_id",
        back_populates="product",
    )
    equivalent_of: Mapped[list["ProductCrossReference"]] = relationship(
        foreign_keys="ProductCrossReference.equivalent_product_id",
        back_populates="equivalent_product",
    )
    stock_receipt_items: Mapped[list["StockReceiptItem"]] = relationship(back_populates="product")
    sale_items: Mapped[list["SaleItem"]] = relationship(back_populates="product")
    inventory_transactions: Mapped[list["InventoryTransaction"]] = relationship(
        back_populates="product"
    )
