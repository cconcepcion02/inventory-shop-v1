from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.product_cross_reference import ProductCrossReference
from app.models.product_image import ProductImage
from app.models.product_note import ProductNote


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _product_loader_options(self) -> tuple:
        return (
            selectinload(Product.images),
            selectinload(Product.notes),
            selectinload(Product.cross_references),
            with_loader_criteria(ProductImage, ProductImage.deleted_at.is_(None)),
            with_loader_criteria(ProductNote, ProductNote.deleted_at.is_(None)),
            with_loader_criteria(
                ProductCrossReference,
                ProductCrossReference.deleted_at.is_(None),
            ),
        )

    async def get_by_id(self, product_id: UUID) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .options(*self._product_loader_options())
            .where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Product | None:
        result = await self.db.execute(
            select(Product)
            .options(*self._product_loader_options())
            .where(Product.sku == sku, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_products(
        self,
        page: int,
        page_size: int,
        search: str | None,
        category_id: UUID | None,
        brand_id: UUID | None,
        is_active: bool | None,
    ) -> tuple[list[Product], int]:
        filters = [Product.deleted_at.is_(None)]
        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Product.name.ilike(pattern),
                    Product.sku.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if brand_id is not None:
            filters.append(Product.brand_id == brand_id)
        if is_active is not None:
            filters.append(Product.is_active == is_active)

        count_result = await self.db.execute(
            select(func.count()).select_from(Product).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Product)
            .options(*self._product_loader_options())
            .where(*filters)
            .order_by(Product.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> Product:
        product = Product(**data)
        self.db.add(product)
        await self.db.flush()
        return product

    async def update(self, product: Product, data: dict) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        await self.db.flush()
        return product

    async def soft_delete(self, product: Product) -> None:
        product.deleted_at = datetime.utcnow()
        await self.db.flush()

    async def get_stock_on_hand(self, product_id: UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(InventoryTransaction.quantity_change), 0)).where(
                InventoryTransaction.product_id == product_id,
                InventoryTransaction.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def add_image(self, product_id: UUID, data: dict) -> ProductImage:
        image = ProductImage(product_id=product_id, **data)
        self.db.add(image)
        await self.db.flush()
        return image

    async def delete_image(self, image_id: UUID) -> None:
        result = await self.db.execute(
            select(ProductImage).where(
                ProductImage.id == image_id,
                ProductImage.deleted_at.is_(None),
            )
        )
        image = result.scalar_one_or_none()
        if image is not None:
            image.deleted_at = datetime.utcnow()
            await self.db.flush()

    async def add_note(self, data: dict) -> ProductNote:
        note = ProductNote(**data)
        self.db.add(note)
        await self.db.flush()
        return note

    async def add_cross_reference(self, data: dict) -> ProductCrossReference:
        product_id = data['product_id']
        equivalent_product_id = data['equivalent_product_id']

        duplicate_result = await self.db.execute(
            select(ProductCrossReference).where(
                ProductCrossReference.deleted_at.is_(None),
                or_(
                    (
                        (ProductCrossReference.product_id == product_id)
                        & (
                            ProductCrossReference.equivalent_product_id
                            == equivalent_product_id
                        )
                    ),
                    (
                        (ProductCrossReference.product_id == equivalent_product_id)
                        & (ProductCrossReference.equivalent_product_id == product_id)
                    ),
                ),
            )
        )
        if duplicate_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Cross reference already exists',
            )

        cross_reference = ProductCrossReference(**data)
        self.db.add(cross_reference)
        await self.db.flush()
        return cross_reference

    async def delete_cross_reference(self, ref_id: UUID) -> None:
        result = await self.db.execute(
            select(ProductCrossReference).where(
                ProductCrossReference.id == ref_id,
                ProductCrossReference.deleted_at.is_(None),
            )
        )
        cross_reference = result.scalar_one_or_none()
        if cross_reference is not None:
            cross_reference.deleted_at = datetime.utcnow()
            await self.db.flush()

    async def search_with_cross_references(self, search: str) -> list[Product]:
        pattern = f"%{search.strip()}%"
        matched_product_ids = select(Product.id.label('id')).where(
            Product.deleted_at.is_(None),
            or_(
                Product.name.ilike(pattern),
                Product.sku.ilike(pattern),
                Product.description.ilike(pattern),
            ),
        )

        related_product_ids = union(
            matched_product_ids,
            select(ProductCrossReference.equivalent_product_id.label('id')).where(
                ProductCrossReference.deleted_at.is_(None),
                ProductCrossReference.product_id.in_(matched_product_ids),
            ),
            select(ProductCrossReference.product_id.label('id')).where(
                ProductCrossReference.deleted_at.is_(None),
                ProductCrossReference.equivalent_product_id.in_(matched_product_ids),
            ),
        ).subquery()

        result = await self.db.execute(
            select(Product)
            .options(*self._product_loader_options())
            .where(
                Product.deleted_at.is_(None),
                Product.id.in_(select(related_product_ids.c.id)),
            )
            .order_by(Product.name.asc())
        )
        return list(result.scalars().unique().all())
