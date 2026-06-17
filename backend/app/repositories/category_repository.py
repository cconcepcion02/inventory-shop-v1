from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: UUID) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.name == name, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Category], int]:
        filters = [Category.deleted_at.is_(None)]
        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(Category.name.ilike(pattern), Category.description.ilike(pattern))
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(Category).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Category)
            .where(*filters)
            .order_by(Category.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> Category:
        category = Category(**data)
        self.db.add(category)
        await self.db.flush()
        return category

    async def update(self, obj: Category, data: dict) -> Category:
        for field, value in data.items():
            setattr(obj, field, value)
        await self.db.flush()
        return obj

    async def soft_delete(self, obj: Category) -> None:
        obj.deleted_at = datetime.utcnow()
        await self.db.flush()
