from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_roles
from app.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.inventory_transaction import InventoryTransactionRead

router = APIRouter(
    prefix='/inventory',
    tags=['inventory'],
    dependencies=[Depends(require_roles('admin'))],
)


@router.get('/transactions', response_model=PaginatedResponse[InventoryTransactionRead])
async def list_transactions(
    product_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[InventoryTransactionRead]:
    repository = InventoryTransactionRepository(db)
    transactions, total = await repository.list_transactions(page, page_size, product_id)
    total_pages = ceil(total / page_size) if total else 0
    return PaginatedResponse[InventoryTransactionRead](
        items=[InventoryTransactionRead.model_validate(transaction) for transaction in transactions],
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )
