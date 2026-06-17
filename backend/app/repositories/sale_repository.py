from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.sale_item import SaleItem


class SaleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, sale_id: UUID) -> Sale | None:
        result = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(Sale.id == sale_id, Sale.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_sale_number(self, sale_number: str) -> Sale | None:
        result = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(Sale.sale_number == sale_number, Sale.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_sales(
        self,
        page: int,
        page_size: int,
        cashier_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[list[Sale], int]:
        filters = [Sale.deleted_at.is_(None)]
        if cashier_id is not None:
            filters.append(Sale.cashier_id == cashier_id)
        if date_from is not None:
            filters.append(Sale.sold_at >= datetime.combine(date_from, time.min))
        if date_to is not None:
            filters.append(Sale.sold_at < datetime.combine(date_to + timedelta(days=1), time.min))

        count_result = await self.db.execute(
            select(func.count()).select_from(Sale).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(*filters)
            .order_by(Sale.sold_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create_sale(self, sale_data: dict, items_data: list[dict]) -> Sale:
        sale = Sale(**sale_data)
        self.db.add(sale)
        await self.db.flush()

        items = [SaleItem(sale_id=sale.id, **item_data) for item_data in items_data]
        self.db.add_all(items)
        await self.db.flush()
        sale.items = items
        return sale

    async def get_daily_sales(self, target_date: date) -> list[Sale]:
        start_at = datetime.combine(target_date, time.min)
        end_at = start_at + timedelta(days=1)
        result = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(
                Sale.deleted_at.is_(None),
                Sale.sold_at >= start_at,
                Sale.sold_at < end_at,
            )
            .order_by(Sale.sold_at.asc())
        )
        return list(result.scalars().all())
