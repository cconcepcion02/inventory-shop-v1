from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID | None,
        action: str,
        resource_type: str,
        resource_id: str | None,
        details: dict | None,
        ip_address: str | None,
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            created_at=datetime.utcnow(),
        )
        self.db.add(audit_log)
        await self.db.flush()
        return audit_log

    async def list_logs(
        self,
        page: int,
        page_size: int,
        resource_type: str | None,
        user_id: UUID | None,
    ) -> tuple[list[AuditLog], int]:
        filters = []
        if resource_type is not None:
            filters.append(AuditLog.resource_type == resource_type)
        if user_id is not None:
            filters.append(AuditLog.user_id == user_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(AuditLog).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(AuditLog)
            .where(*filters)
            .order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
