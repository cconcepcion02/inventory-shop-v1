from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampedSchema


class SaleItemBase(SchemaBase):
    product_id: UUID
    quantity: int = Field(ge=1)
    unit_price: Decimal
    subtotal: Decimal


class SaleItemCreate(SchemaBase):
    product_id: UUID
    quantity: int = Field(ge=1)


class SaleItemRead(TimestampedSchema):
    sale_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SaleBase(SchemaBase):
    sale_number: str
    cashier_id: UUID
    total_amount: Decimal
    amount_tendered: Decimal
    change_amount: Decimal
    notes: str | None = None
    sold_at: datetime


class SaleCreate(SchemaBase):
    sale_number: str | None = None
    cashier_id: UUID | None = None
    total_amount: Decimal | None = None
    amount_tendered: Decimal
    change_amount: Decimal | None = None
    notes: str | None = None
    sold_at: datetime | None = None
    items: list[SaleItemCreate] = Field(default_factory=list)


class SaleUpdate(SchemaBase):
    notes: str | None = None


class SaleRead(TimestampedSchema):
    sale_number: str
    cashier_id: UUID
    total_amount: Decimal
    amount_tendered: Decimal
    change_amount: Decimal
    notes: str | None = None
    sold_at: datetime
    items: list[SaleItemRead] = Field(default_factory=list)
