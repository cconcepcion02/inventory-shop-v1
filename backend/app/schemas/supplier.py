from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.common import SchemaBase, TimestampedSchema


class SupplierBase(SchemaBase):
    name: str = Field(min_length=2, max_length=150)
    contact_person: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SchemaBase):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    contact_person: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    address: str | None = None


class SupplierRead(TimestampedSchema):
    name: str
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
