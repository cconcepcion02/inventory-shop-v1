from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase


class DailySalesItem(SchemaBase):
    sale_number: str
    cashier_id: UUID
    total_amount: Decimal
    sold_at: datetime


class DailySalesReport(SchemaBase):
    date: date
    total_sales: int
    total_revenue: Decimal
    items: list[DailySalesItem] = Field(default_factory=list)


class LowStockItem(SchemaBase):
    product_id: UUID
    sku: str
    name: str
    on_hand: int
    reorder_level: int


class LowStockReport(SchemaBase):
    items: list[LowStockItem] = Field(default_factory=list)
    total: int
