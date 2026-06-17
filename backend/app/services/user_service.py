from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.user import UserCreate, UserRead, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    async def get_user(self, user_id: UUID) -> UserRead:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserRead.model_validate(user)

    async def list_users(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> PaginatedResponse[UserRead]:
        users, total = await self.user_repository.list_users(page, page_size, search)
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[UserRead](
            items=[UserRead.model_validate(user) for user in users],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def create_user(self, data: UserCreate) -> UserRead:
        await self._validate_unique_fields(username=data.username, email=data.email)
        await self._ensure_role_exists(data.role_id)

        payload = data.model_dump(exclude={"password"})
        payload["hashed_password"] = hash_password(data.password)

        user = await self.user_repository.create(payload)
        await self.db.commit()
        await self.db.refresh(user)

        created_user = await self.user_repository.get_by_id(user.id)
        if created_user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to load created user",
            )
        return UserRead.model_validate(created_user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        payload = data.model_dump(exclude_unset=True)
        username = payload.get("username")
        email = payload.get("email")
        role_id = payload.get("role_id") if "role_id" in payload else None

        if username is not None:
            await self._validate_unique_fields(username=username, exclude_user_id=user.id)
        if "email" in payload:
            await self._validate_unique_fields(email=email, exclude_user_id=user.id)
        if "role_id" in payload:
            await self._ensure_role_exists(role_id)

        password = payload.pop("password", None)
        if password is not None:
            payload["hashed_password"] = hash_password(password)

        if payload:
            user = await self.user_repository.update(user, payload)
            await self.db.commit()
            await self.db.refresh(user)

        updated_user = await self.user_repository.get_by_id(user.id)
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to load updated user",
            )
        return UserRead.model_validate(updated_user)

    async def delete_user(self, user_id: UUID) -> MessageResponse:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await self.user_repository.soft_delete(user)
        await self.db.commit()
        await self.db.refresh(user)
        return MessageResponse(message="User deleted successfully")

    async def _validate_unique_fields(
        self,
        username: str | None = None,
        email: str | None = None,
        exclude_user_id: UUID | None = None,
    ) -> None:
        if username is not None:
            existing_user = await self.user_repository.get_by_username(username)
            if existing_user is not None and existing_user.id != exclude_user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists",
                )

        if email is not None:
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user is not None and existing_user.id != exclude_user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )

    async def _ensure_role_exists(self, role_id: UUID | None) -> None:
        if role_id is None:
            return

        role = await self.role_repository.get_by_id(role_id)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
