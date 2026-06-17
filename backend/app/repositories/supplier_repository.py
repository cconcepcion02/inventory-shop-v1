from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        result = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id, Supplier.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Supplier | None:
        result = await self.db.execute(
            select(Supplier)
            .where(Supplier.name == name, Supplier.deleted_at.is_(None))
            .order_by(Supplier.created_at.desc())
        )
        return result.scalars().first()

    async def list_suppliers(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[Supplier], int]:
        filters = [Supplier.deleted_at.is_(None)]
        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Supplier.name.ilike(pattern),
                    Supplier.contact_person.ilike(pattern),
                    Supplier.phone.ilike(pattern),
                    Supplier.email.ilike(pattern),
                    Supplier.address.ilike(pattern),
                )
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(Supplier).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Supplier)
            .where(*filters)
            .order_by(Supplier.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, data: dict) -> Supplier:
        supplier = Supplier(**data)
        self.db.add(supplier)
        await self.db.flush()
        return supplier

    async def update(self, obj: Supplier, data: dict) -> Supplier:
        for field, value in data.items():
            setattr(obj, field, value)
        await self.db.flush()
        return obj

    async def soft_delete(self, obj: Supplier) -> None:
        obj.deleted_at = datetime.utcnow()
        await self.db.flush()
