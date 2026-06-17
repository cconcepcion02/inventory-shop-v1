from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.repositories.sale_repository import SaleRepository
from app.schemas.report import DailySalesItem, DailySalesReport, LowStockItem, LowStockReport


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sale_repository = SaleRepository(db)

    async def get_daily_sales(self, target_date: date) -> DailySalesReport:
        sales = await self.sale_repository.get_daily_sales(target_date)
        total_revenue = sum((sale.total_amount for sale in sales), Decimal('0.00'))
        return DailySalesReport(
            date=target_date,
            total_sales=len(sales),
            total_revenue=total_revenue,
            items=[
                DailySalesItem(
                    sale_number=sale.sale_number,
                    cashier_id=sale.cashier_id,
                    total_amount=sale.total_amount,
                    sold_at=sale.sold_at,
                )
                for sale in sales
            ],
        )

    async def get_low_stock(self, threshold: int | None = None) -> LowStockReport:
        on_hand = func.coalesce(func.sum(InventoryTransaction.quantity_change), 0).label('on_hand')
        result = await self.db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.reorder_level,
                on_hand,
            )
            .outerjoin(
                InventoryTransaction,
                and_(
                    InventoryTransaction.product_id == Product.id,
                    InventoryTransaction.deleted_at.is_(None),
                ),
            )
            .where(Product.deleted_at.is_(None), Product.is_active.is_(True))
            .group_by(Product.id, Product.sku, Product.name, Product.reorder_level)
            .order_by(on_hand.asc(), Product.name.asc())
        )

        items: list[LowStockItem] = []
        for row in result.all():
            current_on_hand = int(row.on_hand)
            limit = threshold if threshold is not None else row.reorder_level
            if current_on_hand <= limit:
                items.append(
                    LowStockItem(
                        product_id=row.id,
                        sku=row.sku,
                        name=row.name,
                        on_hand=current_on_hand,
                        reorder_level=row.reorder_level,
                    )
                )

        return LowStockReport(items=items, total=len(items))
