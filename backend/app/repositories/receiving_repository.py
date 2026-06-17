from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.stock_receipt import StockReceipt
from app.models.stock_receipt_item import StockReceiptItem


class ReceivingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, receipt_id: UUID) -> StockReceipt | None:
        result = await self.db.execute(
            select(StockReceipt)
            .options(selectinload(StockReceipt.items))
            .where(StockReceipt.id == receipt_id, StockReceipt.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_receipt_number(self, receipt_number: str) -> StockReceipt | None:
        result = await self.db.execute(
            select(StockReceipt)
            .options(selectinload(StockReceipt.items))
            .where(
                StockReceipt.receipt_number == receipt_number,
                StockReceipt.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_receipts(
        self,
        page: int,
        page_size: int,
        supplier_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[list[StockReceipt], int]:
        filters = [StockReceipt.deleted_at.is_(None)]
        if supplier_id is not None:
            filters.append(StockReceipt.supplier_id == supplier_id)
        if date_from is not None:
            filters.append(StockReceipt.received_at >= datetime.combine(date_from, time.min))
        if date_to is not None:
            filters.append(
                StockReceipt.received_at < datetime.combine(date_to + timedelta(days=1), time.min)
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(StockReceipt).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(StockReceipt)
            .options(selectinload(StockReceipt.items))
            .where(*filters)
            .order_by(StockReceipt.received_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create_receipt(self, receipt_data: dict, items_data: list[dict]) -> StockReceipt:
        receipt = StockReceipt(**receipt_data)
        self.db.add(receipt)
        await self.db.flush()

        items = [StockReceiptItem(receipt_id=receipt.id, **item_data) for item_data in items_data]
        self.db.add_all(items)
        await self.db.flush()
        receipt.items = items
        return receipt
