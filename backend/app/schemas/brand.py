from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampedSchema


class BrandBase(SchemaBase):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None


class BrandRead(TimestampedSchema):
    name: str
    description: str | None = None
