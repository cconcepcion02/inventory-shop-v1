from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.common import MessageResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def authenticate(self, username: str, password: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user = await self.user_repository.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        return user

    async def login(self, username: str, password: str) -> Token:
        user = await self.authenticate(username, password)
        payload = {"sub": str(user.id), "role": user.role.name if user.role else None}
        return Token(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = decode_token(refresh_token)
            subject = payload.get("sub")
            token_type = payload.get("type")
            if token_type != "refresh" or not subject:
                raise credentials_exception
            user_id = uuid.UUID(subject)
        except (JWTError, ValueError) as exc:
            raise credentials_exception from exc

        user = await self.user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise credentials_exception

        new_access_token = create_access_token(
            {"sub": str(user.id), "role": user.role.name if user.role else None}
        )
        return Token(access_token=new_access_token, refresh_token=refresh_token)

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> MessageResponse:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.hashed_password = hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return MessageResponse(message="Password changed successfully")
