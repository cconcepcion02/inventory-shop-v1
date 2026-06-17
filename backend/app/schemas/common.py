from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(SchemaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class MessageResponse(SchemaBase):
    message: str


class PaginationParams(SchemaBase):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginationMeta(SchemaBase):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(SchemaBase, Generic[T]):
    items: list[T]
    meta: PaginationMeta
