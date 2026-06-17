from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_roles
from app.schemas.report import DailySalesReport, LowStockReport
from app.services.report_service import ReportService

router = APIRouter(
    prefix='/reports',
    tags=['reports'],
    dependencies=[Depends(require_roles('admin'))],
)


@router.get('/daily-sales', response_model=DailySalesReport)
async def get_daily_sales(
    report_date: date | None = Query(default=None, alias='date'),
    db: AsyncSession = Depends(get_db),
) -> DailySalesReport:
    service = ReportService(db)
    return await service.get_daily_sales(report_date or date.today())


@router.get('/low-stock', response_model=LowStockReport)
async def get_low_stock(
    threshold: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> LowStockReport:
    service = ReportService(db)
    return await service.get_low_stock(threshold)
