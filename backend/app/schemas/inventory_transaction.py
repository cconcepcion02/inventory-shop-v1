from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampedSchema


class InventoryTransactionBase(SchemaBase):
    product_id: UUID
    transaction_type: str = Field(pattern='^(receipt|sale|adjustment|return)$')
    quantity_change: int
    reference_id: UUID | None = None
    reference_type: str | None = Field(default=None, pattern='^(sale|receipt)$')
    notes: str | None = None
    created_by: UUID


class InventoryTransactionCreate(InventoryTransactionBase):
    pass


class InventoryTransactionRead(TimestampedSchema):
    product_id: UUID
    transaction_type: str
    quantity_change: int
    reference_id: UUID | None = None
    reference_type: str | None = None
    notes: str | None = None
    created_by: UUID
