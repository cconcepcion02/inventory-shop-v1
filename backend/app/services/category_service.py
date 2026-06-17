from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationMeta


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repository = CategoryRepository(db)

    async def get_category(self, category_id: UUID) -> CategoryRead:
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found',
            )
        return CategoryRead.model_validate(category)

    async def list_categories(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> PaginatedResponse[CategoryRead]:
        categories, total = await self.category_repository.list_categories(
            page,
            page_size,
            search,
        )
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[CategoryRead](
            items=[CategoryRead.model_validate(category) for category in categories],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def create_category(self, data: CategoryCreate) -> CategoryRead:
        existing_category = await self.category_repository.get_by_name(data.name)
        if existing_category is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Category name already exists',
            )

        category = await self.category_repository.create(data.model_dump())
        await self.db.commit()
        await self.db.refresh(category)
        return CategoryRead.model_validate(category)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryRead:
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found',
            )

        payload = data.model_dump(exclude_unset=True)
        name = payload.get('name')
        if name is not None:
            existing_category = await self.category_repository.get_by_name(name)
            if existing_category is not None and existing_category.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Category name already exists',
                )

        if payload:
            category = await self.category_repository.update(category, payload)
            await self.db.commit()
            await self.db.refresh(category)

        return CategoryRead.model_validate(category)

    async def delete_category(self, category_id: UUID) -> MessageResponse:
        category = await self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found',
            )

        await self.category_repository.soft_delete(category)
        await self.db.commit()
        await self.db.refresh(category)
        return MessageResponse(message='Category deleted successfully')
