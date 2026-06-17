from __future__ import annotations

from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.brand_repository import BrandRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.product import (
    ProductCreate,
    ProductCrossReferenceCreate,
    ProductCrossReferenceRead,
    ProductImageCreate,
    ProductImageRead,
    ProductNoteRead,
    ProductRead,
    ProductStockSnapshot,
    ProductUpdate,
)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)
        self.brand_repository = BrandRepository(db)
        self.supplier_repository = SupplierRepository(db)

    async def get_product(self, product_id: UUID) -> ProductRead:
        product = await self._get_existing_product(product_id)
        return await self._build_product_read(product)

    async def list_products(
        self,
        page: int,
        page_size: int,
        search: str | None,
        category_id: UUID | None,
        brand_id: UUID | None,
        is_active: bool | None,
    ) -> PaginatedResponse[ProductRead]:
        products, total = await self.product_repository.list_products(
            page,
            page_size,
            search,
            category_id,
            brand_id,
            is_active,
        )
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[ProductRead](
            items=[ProductRead.model_validate(product) for product in products],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def search_products(self, query: str) -> list[ProductRead]:
        products = await self.product_repository.search_with_cross_references(query)
        return [ProductRead.model_validate(product) for product in products]

    async def create_product(self, data: ProductCreate, created_by: UUID) -> ProductRead:
        del created_by
        existing_product = await self.product_repository.get_by_sku(data.sku)
        if existing_product is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Product SKU already exists',
            )

        await self._ensure_related_entities_exist(
            category_id=data.category_id,
            brand_id=data.brand_id,
            supplier_id=data.supplier_id,
        )

        payload = data.model_dump(exclude={'images'})
        product = await self.product_repository.create(payload)
        for image in data.images:
            await self.product_repository.add_image(product.id, image.model_dump())

        await self.db.commit()
        created_product = await self.product_repository.get_by_id(product.id)
        if created_product is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Unable to load created product',
            )
        return ProductRead.model_validate(created_product)

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductRead:
        product = await self._get_existing_product(product_id)
        payload = data.model_dump(exclude_unset=True)

        sku = payload.get('sku')
        if sku is not None:
            existing_product = await self.product_repository.get_by_sku(sku)
            if existing_product is not None and existing_product.id != product.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Product SKU already exists',
                )

        await self._ensure_related_entities_exist(
            category_id=payload.get('category_id') if 'category_id' in payload else None,
            brand_id=payload.get('brand_id') if 'brand_id' in payload else None,
            supplier_id=payload.get('supplier_id') if 'supplier_id' in payload else None,
        )

        if payload:
            product = await self.product_repository.update(product, payload)
            await self.db.commit()

        updated_product = await self.product_repository.get_by_id(product.id)
        if updated_product is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Unable to load updated product',
            )
        return ProductRead.model_validate(updated_product)

    async def delete_product(self, product_id: UUID) -> MessageResponse:
        product = await self._get_existing_product(product_id)
        await self.product_repository.soft_delete(product)
        await self.db.commit()
        return MessageResponse(message='Product deleted successfully')

    async def get_stock_snapshot(self, product_id: UUID) -> ProductStockSnapshot:
        await self._get_existing_product(product_id)
        on_hand = await self.product_repository.get_stock_on_hand(product_id)
        return ProductStockSnapshot(
            product_id=product_id,
            on_hand=on_hand,
            as_of=datetime.now(timezone.utc),
        )

    async def add_image(self, product_id: UUID, data: ProductImageCreate) -> ProductImageRead:
        await self._get_existing_product(product_id)
        image = await self.product_repository.add_image(product_id, data.model_dump())
        await self.db.commit()
        await self.db.refresh(image)
        return ProductImageRead.model_validate(image)

    async def delete_image(self, product_id: UUID, image_id: UUID) -> MessageResponse:
        product = await self._get_existing_product(product_id)
        image = next((item for item in product.images if item.id == image_id), None)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product image not found',
            )

        await self.product_repository.delete_image(image_id)
        await self.db.commit()
        return MessageResponse(message='Product image deleted successfully')

    async def add_note(
        self,
        product_id: UUID,
        note: str,
        created_by: UUID,
    ) -> ProductNoteRead:
        await self._get_existing_product(product_id)
        product_note = await self.product_repository.add_note(
            {
                'product_id': product_id,
                'note': note,
                'created_by': created_by,
            }
        )
        await self.db.commit()
        await self.db.refresh(product_note)
        return ProductNoteRead.model_validate(product_note)

    async def add_cross_reference(
        self,
        product_id: UUID,
        data: ProductCrossReferenceCreate,
    ) -> ProductCrossReferenceRead:
        await self._get_existing_product(product_id)
        await self._get_existing_product(data.equivalent_product_id)
        if product_id != data.product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Product ID mismatch',
            )
        if product_id == data.equivalent_product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Product cannot reference itself',
            )

        cross_reference = await self.product_repository.add_cross_reference(
            data.model_dump()
        )
        await self.db.commit()
        await self.db.refresh(cross_reference)
        return ProductCrossReferenceRead.model_validate(cross_reference)

    async def delete_cross_reference(
        self,
        product_id: UUID,
        ref_id: UUID,
    ) -> MessageResponse:
        product = await self._get_existing_product(product_id)
        cross_reference = next(
            (item for item in product.cross_references if item.id == ref_id),
            None,
        )
        if cross_reference is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product cross reference not found',
            )

        await self.product_repository.delete_cross_reference(ref_id)
        await self.db.commit()
        return MessageResponse(message='Product cross reference deleted successfully')

    async def _ensure_related_entities_exist(
        self,
        category_id: UUID | None,
        brand_id: UUID | None,
        supplier_id: UUID | None,
    ) -> None:
        if category_id is not None:
            category = await self.category_repository.get_by_id(category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Category not found',
                )

        if brand_id is not None:
            brand = await self.brand_repository.get_by_id(brand_id)
            if brand is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Brand not found',
                )

        if supplier_id is not None:
            supplier = await self.supplier_repository.get_by_id(supplier_id)
            if supplier is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Supplier not found',
                )

    async def _get_existing_product(self, product_id: UUID):
        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found',
            )
        return product

    async def _build_product_read(self, product) -> ProductRead:
        response = ProductRead.model_validate(product)
        if 'stock_on_hand' in ProductRead.model_fields:
            stock_on_hand = await self.product_repository.get_stock_on_hand(product.id)
            response = response.model_copy(update={'stock_on_hand': stock_on_hand})
        return response
