from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampedSchema


class ProductImageBase(SchemaBase):
    url: str = Field(min_length=1, max_length=500)
    is_primary: bool = False
    sort_order: int = 0


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(TimestampedSchema):
    product_id: UUID
    url: str
    is_primary: bool
    sort_order: int


class ProductNoteBase(SchemaBase):
    note: str = Field(min_length=1)


class ProductNoteCreate(ProductNoteBase):
    product_id: UUID
    created_by: UUID


class ProductNoteInput(ProductNoteBase):
    pass


class ProductNoteRead(TimestampedSchema):
    product_id: UUID
    note: str
    created_by: UUID


class ProductCrossReferenceBase(SchemaBase):
    equivalent_product_id: UUID
    note: str | None = Field(default=None, max_length=255)


class ProductCrossReferenceCreate(ProductCrossReferenceBase):
    product_id: UUID


class ProductCrossReferenceRead(TimestampedSchema):
    product_id: UUID
    equivalent_product_id: UUID
    note: str | None = None


class ProductBase(SchemaBase):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category_id: UUID | None = None
    brand_id: UUID | None = None
    supplier_id: UUID | None = None
    cost_price: Decimal
    selling_price: Decimal
    reorder_level: int = 0
    is_active: bool = True


class ProductCreate(ProductBase):
    images: list[ProductImageCreate] = Field(default_factory=list)


class ProductUpdate(SchemaBase):
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category_id: UUID | None = None
    brand_id: UUID | None = None
    supplier_id: UUID | None = None
    cost_price: Decimal | None = None
    selling_price: Decimal | None = None
    reorder_level: int | None = None
    is_active: bool | None = None


class ProductRead(TimestampedSchema):
    sku: str
    name: str
    description: str | None = None
    category_id: UUID | None = None
    brand_id: UUID | None = None
    supplier_id: UUID | None = None
    cost_price: Decimal
    selling_price: Decimal
    reorder_level: int
    is_active: bool
    stock_on_hand: int | None = None
    images: list[ProductImageRead] = Field(default_factory=list)
    notes: list[ProductNoteRead] = Field(default_factory=list)
    cross_references: list[ProductCrossReferenceRead] = Field(default_factory=list)


class ProductStockSnapshot(SchemaBase):
    product_id: UUID
    on_hand: int
    as_of: datetime


class ProductPublicRead(SchemaBase):
    """Public catalog view — no prices, no costs, no quantities."""
    id: UUID
    sku: str
    name: str
    description: str | None = None
    category_id: UUID | None = None
    brand_id: UUID | None = None
    is_active: bool
    in_stock: bool = True  # active products are available; exact qty is hidden
    images: list[ProductImageRead] = Field(default_factory=list)
    created_at: datetime

    @classmethod
    def model_validate(cls, obj: object, **kwargs: object) -> "ProductPublicRead":  # type: ignore[override]
        from app.schemas.product import ProductRead  # avoid circular
        if isinstance(obj, ProductRead):
            return cls(
                id=obj.id,
                sku=obj.sku,
                name=obj.name,
                description=obj.description,
                category_id=obj.category_id,
                brand_id=obj.brand_id,
                is_active=obj.is_active,
                in_stock=obj.is_active,
                images=obj.images,
                created_at=obj.created_at,
            )
        return super().model_validate(obj, **kwargs)  # type: ignore[return-value]
