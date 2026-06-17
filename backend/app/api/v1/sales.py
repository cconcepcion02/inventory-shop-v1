from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.sale import SaleCreate, SaleRead
from app.services.sale_service import SaleService

router = APIRouter(prefix='/sales', tags=['sales'])


@router.post('/', response_model=SaleRead, status_code=status.HTTP_201_CREATED)
async def create_sale(
    payload: SaleCreate,
    current_user: User = Depends(require_roles('admin', 'cashier')),
    db: AsyncSession = Depends(get_db),
) -> SaleRead:
    service = SaleService(db)
    return await service.create_sale(payload, current_user)


@router.get('/', response_model=PaginatedResponse[SaleRead])
async def list_sales(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: User = Depends(require_roles('admin', 'cashier')),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SaleRead]:
    service = SaleService(db)
    role_name = current_user.role.name if current_user.role else None
    cashier_id = None if role_name == 'admin' else current_user.id
    return await service.list_sales(page, page_size, cashier_id, date_from, date_to)


@router.get('/{sale_id}', response_model=SaleRead)
async def get_sale(
    sale_id: UUID,
    current_user: User = Depends(require_roles('admin', 'cashier')),
    db: AsyncSession = Depends(get_db),
) -> SaleRead:
    service = SaleService(db)
    sale = await service.get_sale(sale_id)
    role_name = current_user.role.name if current_user.role else None
    if role_name != 'admin' and sale.cashier_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient permissions',
        )
    return sale
