from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[User], int]:
        filters = [User.deleted_at.is_(None)]
        if search:
            pattern = f"%{search.strip()}%"
            filters.append(or_(User.username.ilike(pattern), User.email.ilike(pattern)))

        count_result = await self.db.execute(
            select(func.count()).select_from(User).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(*filters)
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User, data: dict) -> User:
        for field, value in data.items():
            setattr(user, field, value)
        await self.db.flush()
        return user

    async def soft_delete(self, user: User) -> None:
        user.deleted_at = datetime.utcnow()
        await self.db.flush()
