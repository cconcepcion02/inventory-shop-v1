from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db, require_roles
from app.schemas.brand import BrandCreate, BrandRead, BrandUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.brand_service import BrandService

router = APIRouter(
    prefix='/brands',
    tags=['brands'],
    dependencies=[Depends(get_current_active_user)],
)


@router.get('/', response_model=PaginatedResponse[BrandRead])
async def list_brands(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[BrandRead]:
    service = BrandService(db)
    return await service.list_brands(page, page_size, search)


@router.post('/', response_model=BrandRead, status_code=status.HTTP_201_CREATED)
async def create_brand(
    payload: BrandCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles('admin')),
) -> BrandRead:
    service = BrandService(db)
    return await service.create_brand(payload)


@router.get('/{brand_id}', response_model=BrandRead)
async def get_brand(
    brand_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BrandRead:
    service = BrandService(db)
    return await service.get_brand(brand_id)


@router.put('/{brand_id}', response_model=BrandRead)
async def update_brand(
    brand_id: UUID,
    payload: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles('admin')),
) -> BrandRead:
    service = BrandService(db)
    return await service.update_brand(brand_id, payload)


@router.delete('/{brand_id}', response_model=MessageResponse)
async def delete_brand(
    brand_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles('admin')),
) -> MessageResponse:
    service = BrandService(db)
    return await service.delete_brand(brand_id)
