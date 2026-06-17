from __future__ import annotations

from pydantic import Field

from app.schemas.common import SchemaBase


class LoginRequest(SchemaBase):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(SchemaBase):
    refresh_token: str


class ChangePasswordRequest(SchemaBase):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class TokenPayload(SchemaBase):
    sub: str | None = None
    exp: int | None = None
    type: str | None = None


class Token(SchemaBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
