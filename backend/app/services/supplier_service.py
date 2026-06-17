from __future__ import annotations

from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.supplier_repository import SupplierRepository
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate


class SupplierService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.supplier_repository = SupplierRepository(db)

    async def get_supplier(self, supplier_id: UUID) -> SupplierRead:
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Supplier not found',
            )
        return SupplierRead.model_validate(supplier)

    async def list_suppliers(
        self,
        page: int,
        page_size: int,
        search: str | None,
    ) -> PaginatedResponse[SupplierRead]:
        suppliers, total = await self.supplier_repository.list_suppliers(
            page,
            page_size,
            search,
        )
        total_pages = ceil(total / page_size) if total else 0
        return PaginatedResponse[SupplierRead](
            items=[SupplierRead.model_validate(supplier) for supplier in suppliers],
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    async def create_supplier(self, data: SupplierCreate) -> SupplierRead:
        supplier = await self.supplier_repository.create(data.model_dump())
        await self.db.commit()
        await self.db.refresh(supplier)
        return SupplierRead.model_validate(supplier)

    async def update_supplier(self, supplier_id: UUID, data: SupplierUpdate) -> SupplierRead:
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Supplier not found',
            )

        payload = data.model_dump(exclude_unset=True)
        if payload:
            supplier = await self.supplier_repository.update(supplier, payload)
            await self.db.commit()
            await self.db.refresh(supplier)

        return SupplierRead.model_validate(supplier)

    async def delete_supplier(self, supplier_id: UUID) -> MessageResponse:
        supplier = await self.supplier_repository.get_by_id(supplier_id)
        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Supplier not found',
            )

        await self.supplier_repository.soft_delete(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)
        return MessageResponse(message='Supplier deleted successfully')
