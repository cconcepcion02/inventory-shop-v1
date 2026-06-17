from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductPublicRead
from app.services.product_service import ProductService

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/products", response_model=PaginatedResponse[ProductPublicRead])
async def list_public_products(
    search: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    brand_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ProductPublicRead]:
    """Public product catalog — no auth required. Prices and costs are hidden."""
    service = ProductService(db)
    result = await service.list_products(
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        brand_id=brand_id,
        is_active=True,
    )
    return PaginatedResponse[ProductPublicRead](
        items=[ProductPublicRead.model_validate(p) for p in result.items],
        meta=result.meta,
    )


@router.get("/products/search", response_model=list[ProductPublicRead])
async def search_public_products(
    q: str = Query(min_length=1),
    db: AsyncSession = Depends(get_db),
) -> list[ProductPublicRead]:
    """Cross-reference product search — public, no auth required."""
    service = ProductService(db)
    results = await service.search_products(q)
    return [ProductPublicRead.model_validate(p) for p in results]
