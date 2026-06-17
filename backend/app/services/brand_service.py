from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.brand_repository import BrandRepository
from app.schemas.brand import BrandCreate, BrandRead, BrandUpdate
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationMeta


class BrandService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.brand_repository = BrandRepository(db)

    async def get_brand(self, brand_id: UUID) -> BrandRead:
        brand = await self.brand_repository.get_by_id(brand_id)
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Brand not found',
            )
        return BrandRead.model_validate(brand)

    async def list_brands(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> PaginatedResponse[BrandRead]:
        brands, total = await self.brand_repository.list_brands(page, page_size, search)
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[BrandRead](
            items=[BrandRead.model_validate(brand) for brand in brands],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def create_brand(self, data: BrandCreate) -> BrandRead:
        existing_brand = await self.brand_repository.get_by_name(data.name)
        if existing_brand is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Brand name already exists',
            )

        brand = await self.brand_repository.create(data.model_dump())
        await self.db.commit()
        await self.db.refresh(brand)
        return BrandRead.model_validate(brand)

    async def update_brand(self, brand_id: UUID, data: BrandUpdate) -> BrandRead:
        brand = await self.brand_repository.get_by_id(brand_id)
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Brand not found',
            )

        payload = data.model_dump(exclude_unset=True)
        name = payload.get('name')
        if name is not None:
            existing_brand = await self.brand_repository.get_by_name(name)
            if existing_brand is not None and existing_brand.id != brand.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Brand name already exists',
                )

        if payload:
            brand = await self.brand_repository.update(brand, payload)
            await self.db.commit()
            await self.db.refresh(brand)

        return BrandRead.model_validate(brand)

    async def delete_brand(self, brand_id: UUID) -> MessageResponse:
        brand = await self.brand_repository.get_by_id(brand_id)
        if brand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Brand not found',
            )

        await self.brand_repository.soft_delete(brand)
        await self.db.commit()
        await self.db.refresh(brand)
        return MessageResponse(message='Brand deleted successfully')
