from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand


class BrandRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, brand_id: UUID) -> Brand | None:
        result = await self.db.execute(
            select(Brand).where(Brand.id == brand_id, Brand.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Brand | None:
        result = await self.db.execute(
            select(Brand).where(Brand.name == name, Brand.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_brands(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Brand], int]:
        filters = [Brand.deleted_at.is_(None)]
        if search:
            pattern = f"%{search.strip()}%"
            filters.append(or_(Brand.name.ilike(pattern), Brand.description.ilike(pattern)))

        count_result = await self.db.execute(
            select(func.count()).select_from(Brand).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Brand)
            .where(*filters)
            .order_by(Brand.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> Brand:
        brand = Brand(**data)
        self.db.add(brand)
        await self.db.flush()
        return brand

    async def update(self, obj: Brand, data: dict) -> Brand:
        for field, value in data.items():
            setattr(obj, field, value)
        await self.db.flush()
        return obj

    async def soft_delete(self, obj: Brand) -> None:
        obj.deleted_at = datetime.utcnow()
        await self.db.flush()
