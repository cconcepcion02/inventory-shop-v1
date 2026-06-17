from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.brands import router as brands_router
from app.api.v1.categories import router as categories_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.products import router as products_router
from app.api.v1.public import router as public_router
from app.api.v1.receiving import router as receiving_router
from app.api.v1.reports import router as reports_router
from app.api.v1.sales import router as sales_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.users import router as users_router

router = APIRouter()


@router.get("/health", tags=["system"])
async def v1_healthcheck() -> dict[str, str]:
    return {"status": "ok", "version": "v1"}


router.include_router(auth_router)
router.include_router(users_router)
router.include_router(products_router)
router.include_router(categories_router)
router.include_router(brands_router)
router.include_router(suppliers_router)
router.include_router(sales_router)
router.include_router(receiving_router)
router.include_router(reports_router)
router.include_router(inventory_router)
router.include_router(public_router)
