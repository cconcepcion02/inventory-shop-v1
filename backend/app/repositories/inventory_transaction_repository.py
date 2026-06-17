from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_transaction import InventoryTransaction


class InventoryTransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> InventoryTransaction:
        transaction = InventoryTransaction(**data)
        self.db.add(transaction)
        await self.db.flush()
        return transaction

    async def list_by_product(
        self,
        product_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[InventoryTransaction], int]:
        filters = [
            InventoryTransaction.product_id == product_id,
            InventoryTransaction.deleted_at.is_(None),
        ]
        count_result = await self.db.execute(
            select(func.count()).select_from(InventoryTransaction).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(InventoryTransaction)
            .where(*filters)
            .order_by(InventoryTransaction.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def list_transactions(
        self,
        page: int,
        page_size: int,
        product_id: UUID | None = None,
    ) -> tuple[list[InventoryTransaction], int]:
        filters = [InventoryTransaction.deleted_at.is_(None)]
        if product_id is not None:
            filters.append(InventoryTransaction.product_id == product_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(InventoryTransaction).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(InventoryTransaction)
            .where(*filters)
            .order_by(InventoryTransaction.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_stock_on_hand(self, product_id: UUID) -> int:
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(InventoryTransaction.quantity_change), 0)
            ).where(
                InventoryTransaction.product_id == product_id,
                InventoryTransaction.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())
