from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.stock_receipt import StockReceiptCreate, StockReceiptRead
from app.services.receiving_service import ReceivingService

router = APIRouter(
    prefix='/receiving',
    tags=['receiving'],
    dependencies=[Depends(require_roles('admin'))],
)


@router.post('/', response_model=StockReceiptRead, status_code=status.HTTP_201_CREATED)
async def receive_stock(
    payload: StockReceiptCreate,
    current_user: User = Depends(require_roles('admin')),
    db: AsyncSession = Depends(get_db),
) -> StockReceiptRead:
    service = ReceivingService(db)
    return await service.receive_stock(payload, current_user)


@router.get('/', response_model=PaginatedResponse[StockReceiptRead])
async def list_receipts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    supplier_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[StockReceiptRead]:
    service = ReceivingService(db)
    return await service.list_receipts(page, page_size, supplier_id, date_from, date_to)


@router.get('/{receipt_id}', response_model=StockReceiptRead)
async def get_receipt(
    receipt_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> StockReceiptRead:
    service = ReceivingService(db)
    return await service.get_receipt(receipt_id)
