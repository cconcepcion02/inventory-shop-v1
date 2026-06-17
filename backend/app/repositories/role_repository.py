from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, role_id: UUID) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.name == name, Role.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_roles(self) -> list[Role]:
        result = await self.db.execute(
            select(Role).where(Role.deleted_at.is_(None)).order_by(Role.name.asc())
        )
        return list(result.scalars().all())

    async def create(self, name: str) -> Role:
        role = Role(name=name)
        self.db.add(role)
        await self.db.flush()
        return role
