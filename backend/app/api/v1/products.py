from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db, require_roles
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductCrossReferenceCreate,
    ProductCrossReferenceRead,
    ProductImageCreate,
    ProductImageRead,
    ProductNoteInput,
    ProductNoteRead,
    ProductRead,
    ProductStockSnapshot,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(
    prefix='/products',
    tags=['products'],
    dependencies=[Depends(get_current_active_user)],
)


@router.get('/', response_model=PaginatedResponse[ProductRead])
async def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    brand_id: UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ProductRead]:
    service = ProductService(db)
    return await service.list_products(
        page,
        page_size,
        search,
        category_id,
        brand_id,
        is_active,
    )


@router.get('/search', response_model=list[ProductRead])
async def search_products(
    q: str = Query(min_length=1),
    db: AsyncSession = Depends(get_db),
) -> list[ProductRead]:
    service = ProductService(db)
    return await service.search_products(q)


@router.post('/', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles('admin')),
) -> ProductRead:
    service = ProductService(db)
    return await service.create_product(payload, current_user.id)


@router.get('/{product_id}', response_model=ProductRead)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductRead:
    service = ProductService(db)
    return await service.get_product(product_id)


@router.put('/{product_id}', response_model=ProductRead)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles('admin')),
) -> ProductRead:
    service = ProductService(db)
    return await service.update_product(product_id, payload)


@router.delete('/{product_id}', response_model=MessageResponse)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles('admin')),
) -> MessageResponse:
    service = ProductService(db)
    return await service.delete_product(product_id)


@router.get('/{product_id}/stock', response_model=ProductStockSnapshot)
async def get_stock_snapshot(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductStockSnapshot:
    service = ProductService(db)
    return await service.get_stock_snapshot(product_id)


@router.post('/{product_id}/images', response_model=ProductImageRead, status_code=status.HTTP_201_CREATED)
async def add_image(
    product_id: UUID,
    payload: ProductImageCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles('admin')),
) -> ProductImageRead:
    service = ProductService(db)
    return await service.add_image(product_id, payload)


@router.delete('/{product_id}/images/{image_id}', response_model=MessageResponse)
async def delete_image(
    product_id: UUID,
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles('admin')),
) -> MessageResponse:
    service = ProductService(db)
    return await service.delete_image(product_id, image_id)


@router.post('/{product_id}/notes', response_model=ProductNoteRead, status_code=status.HTTP_201_CREATED)
async def add_note(
    product_id: UUID,
    payload: ProductNoteInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProductNoteRead:
    service = ProductService(db)
    return await service.add_note(product_id, payload.note, current_user.id)


@router.post(
    '/{product_id}/cross-references',
    response_model=ProductCrossReferenceRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_cross_reference(
    product_id: UUID,
    payload: ProductCrossReferenceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles('admin')),
) -> ProductCrossReferenceRead:
    service = ProductService(db)
    return await service.add_cross_reference(product_id, payload)


@router.delete('/{product_id}/cross-references/{ref_id}', response_model=MessageResponse)
async def delete_cross_reference(
    product_id: UUID,
    ref_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles('admin')),
) -> MessageResponse:
    service = ProductService(db)
    return await service.delete_cross_reference(product_id, ref_id)
