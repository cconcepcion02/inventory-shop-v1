from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampedSchema


class StockReceiptItemBase(SchemaBase):
    product_id: UUID
    quantity: int = Field(ge=1)
    unit_cost: Decimal


class StockReceiptItemCreate(StockReceiptItemBase):
    pass


class StockReceiptItemRead(TimestampedSchema):
    receipt_id: UUID
    product_id: UUID
    quantity: int
    unit_cost: Decimal


class StockReceiptBase(SchemaBase):
    receipt_number: str
    supplier_id: UUID | None = None
    received_by: UUID
    notes: str | None = None
    received_at: datetime


class StockReceiptCreate(SchemaBase):
    receipt_number: str | None = None
    supplier_id: UUID | None = None
    received_by: UUID | None = None
    notes: str | None = None
    received_at: datetime | None = None
    items: list[StockReceiptItemCreate] = Field(default_factory=list)


class StockReceiptUpdate(SchemaBase):
    supplier_id: UUID | None = None
    received_by: UUID | None = None
    notes: str | None = None
    received_at: datetime | None = None


class StockReceiptRead(TimestampedSchema):
    receipt_number: str
    supplier_id: UUID | None = None
    received_by: UUID
    notes: str | None = None
    received_at: datetime
    items: list[StockReceiptItemRead] = Field(default_factory=list)
