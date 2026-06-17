from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_db, require_roles
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.category_service import CategoryService

router = APIRouter(
    prefix='/categories',
    tags=['categories'],
    dependencies=[Depends(get_current_active_user)],
)


@router.get('/', response_model=PaginatedResponse[CategoryRead])
async def list_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CategoryRead]:
    service = CategoryService(db)
    return await service.list_categories(page, page_size, search)


@router.post('/', response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles('admin')),
) -> CategoryRead:
    service = CategoryService(db)
    return await service.create_category(payload)


@router.get('/{category_id}', response_model=CategoryRead)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CategoryRead:
    service = CategoryService(db)
    return await service.get_category(category_id)


@router.put('/{category_id}', response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles('admin')),
) -> CategoryRead:
    service = CategoryService(db)
    return await service.update_category(category_id, payload)


@router.delete('/{category_id}', response_model=MessageResponse)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_roles('admin')),
) -> MessageResponse:
    service = CategoryService(db)
    return await service.delete_category(category_id)
