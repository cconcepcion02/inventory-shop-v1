from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.repositories.sale_repository import SaleRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.sale import SaleCreate, SaleRead


class SaleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sale_repository = SaleRepository(db)
        self.inventory_transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditRepository(db)

    async def create_sale(self, data: SaleCreate, cashier: User) -> SaleRead:
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Sale must contain at least one item',
            )

        product_ids = list({item.product_id for item in data.items})
        products_result = await self.db.execute(
            select(Product).where(Product.id.in_(product_ids), Product.deleted_at.is_(None))
        )
        products = {product.id: product for product in products_result.scalars().all()}

        requested_quantities: dict[UUID, int] = defaultdict(int)
        for item in data.items:
            requested_quantities[item.product_id] += item.quantity

        for product_id, requested_quantity in requested_quantities.items():
            product = products.get(product_id)
            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Product {product_id} not found',
                )
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Product {product.sku} is inactive',
                )
            on_hand = await self.inventory_transaction_repository.get_stock_on_hand(product_id)
            if on_hand < requested_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Insufficient stock for product {product.sku}',
                )

        sale_number = data.sale_number or await self._generate_sale_number()
        if data.sale_number is not None:
            existing_sale = await self.sale_repository.get_by_sale_number(data.sale_number)
            if existing_sale is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Sale number already exists',
                )

        total_amount = Decimal('0.00')
        items_payload: list[dict] = []
        for item in data.items:
            product = products[item.product_id]
            unit_price = product.selling_price
            subtotal = unit_price * item.quantity
            total_amount += subtotal
            items_payload.append(
                {
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal,
                }
            )

        if data.amount_tendered < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Amount tendered is less than total amount',
            )

        sold_at = data.sold_at or datetime.utcnow()
        change_amount = data.amount_tendered - total_amount
        sale_payload = {
            'sale_number': sale_number,
            'cashier_id': cashier.id,
            'total_amount': total_amount,
            'amount_tendered': data.amount_tendered,
            'change_amount': change_amount,
            'notes': data.notes,
            'sold_at': sold_at,
        }

        try:
            sale = await self.sale_repository.create_sale(sale_payload, items_payload)
            for item_payload in items_payload:
                await self.inventory_transaction_repository.create(
                    {
                        'product_id': item_payload['product_id'],
                        'transaction_type': 'sale',
                        'quantity_change': -item_payload['quantity'],
                        'reference_id': sale.id,
                        'reference_type': 'sale',
                        'notes': f'Sale {sale.sale_number}',
                        'created_by': cashier.id,
                    }
                )
            await self.audit_repository.create(
                user_id=cashier.id,
                action='create_sale',
                resource_type='sale',
                resource_id=str(sale.id),
                details={
                    'sale_number': sale.sale_number,
                    'total_amount': str(total_amount),
                    'item_count': len(items_payload),
                },
                ip_address=None,
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        created_sale = await self.sale_repository.get_by_id(sale.id)
        if created_sale is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Unable to load created sale',
            )
        return SaleRead.model_validate(created_sale)

    async def get_sale(self, sale_id: UUID) -> SaleRead:
        sale = await self.sale_repository.get_by_id(sale_id)
        if sale is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Sale not found',
            )
        return SaleRead.model_validate(sale)

    async def list_sales(
        self,
        page: int,
        page_size: int,
        cashier_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> PaginatedResponse[SaleRead]:
        sales, total = await self.sale_repository.list_sales(
            page,
            page_size,
            cashier_id,
            date_from,
            date_to,
        )
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[SaleRead](
            items=[SaleRead.model_validate(sale) for sale in sales],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def _generate_sale_number(self) -> str:
        while True:
            candidate = f"SALE-{date.today().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            if await self.sale_repository.get_by_sale_number(candidate) is None:
                return candidate
