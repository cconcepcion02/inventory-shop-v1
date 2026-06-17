from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_roles
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.services.supplier_service import SupplierService

router = APIRouter(
    prefix='/suppliers',
    tags=['suppliers'],
    dependencies=[Depends(require_roles('admin'))],
)


@router.get('/', response_model=PaginatedResponse[SupplierRead])
async def list_suppliers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SupplierRead]:
    service = SupplierService(db)
    return await service.list_suppliers(page, page_size, search)


@router.post('/', response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    db: AsyncSession = Depends(get_db),
) -> SupplierRead:
    service = SupplierService(db)
    return await service.create_supplier(payload)


@router.get('/{supplier_id}', response_model=SupplierRead)
async def get_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SupplierRead:
    service = SupplierService(db)
    return await service.get_supplier(supplier_id)


@router.put('/{supplier_id}', response_model=SupplierRead)
async def update_supplier(
    supplier_id: UUID,
    payload: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
) -> SupplierRead:
    service = SupplierService(db)
    return await service.update_supplier(supplier_id, payload)


@router.delete('/{supplier_id}', response_model=MessageResponse)
async def delete_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = SupplierService(db)
    return await service.delete_supplier(supplier_id)
