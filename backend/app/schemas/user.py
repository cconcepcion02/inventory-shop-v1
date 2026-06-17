from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import EmailStr, Field, model_validator

from app.schemas.common import SchemaBase, TimestampedSchema


class UserBase(SchemaBase):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr | None = None
    is_active: bool = True
    role_id: UUID | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(SchemaBase):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    is_active: bool | None = None
    role_id: UUID | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(TimestampedSchema):
    username: str
    email: str | None = None  # str (not EmailStr) — no validation needed on output
    is_active: bool
    role_id: UUID | None = None
    role_name: str | None = None

    @model_validator(mode="before")
    @classmethod
    def populate_role_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "role_name" not in data:
                role = data.get("role")
                data = data.copy()
                data["role_name"] = getattr(role, "name", None) if role is not None else None
            return data

        role = getattr(data, "role", None)
        role_name = getattr(role, "name", None) if role is not None else None
        return {
            "id": getattr(data, "id"),
            "username": getattr(data, "username"),
            "email": getattr(data, "email"),
            "is_active": getattr(data, "is_active"),
            "role_id": getattr(data, "role_id"),
            "role_name": role_name,
            "created_at": getattr(data, "created_at"),
            "updated_at": getattr(data, "updated_at"),
            "deleted_at": getattr(data, "deleted_at", None),
        }


class UserMeRead(UserRead):
    pass
