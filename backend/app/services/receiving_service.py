from __future__ import annotations

import random
from datetime import date, datetime
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.repositories.receiving_repository import ReceivingRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.stock_receipt import StockReceiptCreate, StockReceiptRead


class ReceivingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.receiving_repository = ReceivingRepository(db)
        self.inventory_transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditRepository(db)

    async def receive_stock(self, data: StockReceiptCreate, received_by: User) -> StockReceiptRead:
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Receipt must contain at least one item',
            )

        product_ids = list({item.product_id for item in data.items})
        products_result = await self.db.execute(
            select(Product).where(Product.id.in_(product_ids), Product.deleted_at.is_(None))
        )
        products = {product.id: product for product in products_result.scalars().all()}

        for item in data.items:
            if products.get(item.product_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Product {item.product_id} not found',
                )

        receipt_number = data.receipt_number or await self._generate_receipt_number()
        if data.receipt_number is not None:
            existing_receipt = await self.receiving_repository.get_by_receipt_number(data.receipt_number)
            if existing_receipt is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Receipt number already exists',
                )

        receipt_payload = {
            'receipt_number': receipt_number,
            'supplier_id': data.supplier_id,
            'received_by': received_by.id,
            'notes': data.notes,
            'received_at': data.received_at or datetime.utcnow(),
        }
        items_payload = [
            {
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_cost': item.unit_cost,
            }
            for item in data.items
        ]

        try:
            receipt = await self.receiving_repository.create_receipt(receipt_payload, items_payload)
            for item_payload in items_payload:
                await self.inventory_transaction_repository.create(
                    {
                        'product_id': item_payload['product_id'],
                        'transaction_type': 'receipt',
                        'quantity_change': item_payload['quantity'],
                        'reference_id': receipt.id,
                        'reference_type': 'receipt',
                        'notes': f'Receipt {receipt.receipt_number}',
                        'created_by': received_by.id,
                    }
                )
            await self.audit_repository.create(
                user_id=received_by.id,
                action='receive_stock',
                resource_type='stock_receipt',
                resource_id=str(receipt.id),
                details={
                    'receipt_number': receipt.receipt_number,
                    'item_count': len(items_payload),
                },
                ip_address=None,
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise

        created_receipt = await self.receiving_repository.get_by_id(receipt.id)
        if created_receipt is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Unable to load created receipt',
            )
        return StockReceiptRead.model_validate(created_receipt)

    async def get_receipt(self, receipt_id: UUID) -> StockReceiptRead:
        receipt = await self.receiving_repository.get_by_id(receipt_id)
        if receipt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Receipt not found',
            )
        return StockReceiptRead.model_validate(receipt)

    async def list_receipts(
        self,
        page: int,
        page_size: int,
        supplier_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> PaginatedResponse[StockReceiptRead]:
        receipts, total = await self.receiving_repository.list_receipts(
            page,
            page_size,
            supplier_id,
            date_from,
            date_to,
        )
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[StockReceiptRead](
            items=[StockReceiptRead.model_validate(receipt) for receipt in receipts],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def _generate_receipt_number(self) -> str:
        while True:
            candidate = f"RCV-{date.today().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            if await self.receiving_repository.get_by_receipt_number(candidate) is None:
                return candidate
