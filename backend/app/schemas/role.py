from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaBase, TimestampedSchema


class RoleBase(SchemaBase):
    name: str = Field(min_length=2, max_length=50)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=2, max_length=50)


class RoleRead(TimestampedSchema):
    name: str
