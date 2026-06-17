#!/usr/bin/env python3
"""
Seed script: creates initial roles, admin user, and sample data.
Run with: python scripts/seed.py
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.models import Brand, Category, InventoryTransaction, Product, ProductCrossReference, Role, Supplier, User

ROOT_DIR = Path(__file__).resolve().parents[1]


def get_session_resources() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    load_dotenv(ROOT_DIR / ".env")

    from app.core.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
    return engine, session_factory


async def get_or_create_role(session: AsyncSession, name: str) -> Role:
    role = await session.scalar(select(Role).where(Role.name == name))
    if role is None:
        role = Role(name=name)
        session.add(role)
        await session.flush()
    return role


async def get_or_create_category(session: AsyncSession, name: str) -> Category:
    category = await session.scalar(select(Category).where(Category.name == name))
    if category is None:
        category = Category(name=name)
        session.add(category)
        await session.flush()
    return category


async def get_or_create_brand(session: AsyncSession, name: str) -> Brand:
    brand = await session.scalar(select(Brand).where(Brand.name == name))
    if brand is None:
        brand = Brand(name=name)
        session.add(brand)
        await session.flush()
    return brand


async def get_or_create_supplier(session: AsyncSession) -> Supplier:
    supplier = await session.scalar(select(Supplier).where(Supplier.name == "Default Supplier"))
    if supplier is None:
        supplier = Supplier(
            name="Default Supplier",
            contact_person="John Doe",
            phone="+63 912 345 6789",
            email="supplier@example.com",
        )
        session.add(supplier)
        await session.flush()
        return supplier

    supplier.contact_person = supplier.contact_person or "John Doe"
    supplier.phone = supplier.phone or "+63 912 345 6789"
    supplier.email = supplier.email or "supplier@example.com"
    await session.flush()
    return supplier


async def seed() -> None:
    engine, session_factory = get_session_resources()

    categories_map: dict[str, Category] = {}
    brands_map: dict[str, Brand] = {}
    products_map: dict[str, Product] = {}

    try:
        async with session_factory() as session:
            try:
                admin_role = await get_or_create_role(session, "admin")
                await get_or_create_role(session, "cashier")
                await session.commit()
                print("✓ Created roles")

                from app.core.security import hash_password
                admin_user = await session.scalar(select(User).where(User.username == "admin"))
                admin_password_hash = hash_password("Admin@1234")
                if admin_user is None:
                    admin_user = User(
                        username="admin",
                        email="admin@inventory.local",
                        hashed_password=admin_password_hash,
                        is_active=True,
                        role_id=admin_role.id,
                    )
                    session.add(admin_user)
                else:
                    admin_user.email = "admin@inventory.local"
                    admin_user.is_active = True
                    admin_user.role_id = admin_role.id
                    admin_user.hashed_password = admin_password_hash
                await session.commit()
                await session.refresh(admin_user)
                print("✓ Created admin user")

                for category_name in [
                    "Engine Parts",
                    "Brakes",
                    "Suspension",
                    "Electrical",
                    "Body Parts",
                ]:
                    categories_map[category_name] = await get_or_create_category(session, category_name)
                await session.commit()
                print("✓ Created categories")

                for brand_name in ["SKF", "NSK", "NTN", "NGK", "Bosch"]:
                    brands_map[brand_name] = await get_or_create_brand(session, brand_name)
                await session.commit()
                print("✓ Created brands")

                supplier = await get_or_create_supplier(session)
                await session.commit()
                await session.refresh(supplier)
                print("✓ Created supplier")

                product_specs = [
                {
                    "sku": "SKF-6201",
                    "name": "SKF Deep Groove Ball Bearing 6201",
                    "brand": "SKF",
                    "category": "Engine Parts",
                    "cost_price": Decimal("85.00"),
                    "selling_price": Decimal("120.00"),
                    "reorder_level": 10,
                },
                {
                    "sku": "NSK-6201",
                    "name": "NSK Deep Groove Ball Bearing 6201",
                    "brand": "NSK",
                    "category": "Engine Parts",
                    "cost_price": Decimal("80.00"),
                    "selling_price": Decimal("115.00"),
                    "reorder_level": 10,
                },
                {
                    "sku": "NTN-6201",
                    "name": "NTN Deep Groove Ball Bearing 6201",
                    "brand": "NTN",
                    "category": "Engine Parts",
                    "cost_price": Decimal("78.00"),
                    "selling_price": Decimal("110.00"),
                    "reorder_level": 10,
                },
                {
                    "sku": "NGK-BP6ES",
                    "name": "NGK Standard Spark Plug BP6ES",
                    "brand": "NGK",
                    "category": "Electrical",
                    "cost_price": Decimal("45.00"),
                    "selling_price": Decimal("75.00"),
                    "reorder_level": 20,
                },
                {
                    "sku": "NGK-CR8E",
                    "name": "NGK Iridium Spark Plug CR8E",
                    "brand": "NGK",
                    "category": "Electrical",
                    "cost_price": Decimal("120.00"),
                    "selling_price": Decimal("195.00"),
                    "reorder_level": 15,
                },
                {
                    "sku": "BSH-OILF-01",
                    "name": "Bosch Oil Filter Universal",
                    "brand": "Bosch",
                    "category": "Engine Parts",
                    "cost_price": Decimal("55.00"),
                    "selling_price": Decimal("90.00"),
                    "reorder_level": 15,
                },
                {
                    "sku": "BRK-PAD-FRONT-01",
                    "name": "Front Brake Pad Set Generic",
                    "brand": None,
                    "category": "Brakes",
                    "cost_price": Decimal("150.00"),
                    "selling_price": Decimal("250.00"),
                    "reorder_level": 8,
                },
                {
                    "sku": "SUSP-FORK-OIL-10W",
                    "name": "Fork Oil 10W 1L",
                    "brand": None,
                    "category": "Suspension",
                    "cost_price": Decimal("180.00"),
                    "selling_price": Decimal("280.00"),
                    "reorder_level": 5,
                },
                {
                    "sku": "BODY-MIRROR-L-01",
                    "name": "Left Side Mirror Universal",
                    "brand": None,
                    "category": "Body Parts",
                    "cost_price": Decimal("200.00"),
                    "selling_price": Decimal("350.00"),
                    "reorder_level": 5,
                },
                {
                    "sku": "ELEC-BATT-12V7A",
                    "name": "12V 7Ah Motorcycle Battery",
                    "brand": None,
                    "category": "Electrical",
                    "cost_price": Decimal("550.00"),
                    "selling_price": Decimal("850.00"),
                    "reorder_level": 3,
                },
            ]

                for spec in product_specs:
                    product = await session.scalar(select(Product).where(Product.sku == spec["sku"]))
                    if product is None:
                        product = Product(sku=spec["sku"])
                        session.add(product)
                    product.name = spec["name"]
                    product.description = None
                    product.category_id = categories_map[spec["category"]].id
                    product.brand_id = brands_map[spec["brand"]].id if spec["brand"] else None
                    product.supplier_id = supplier.id
                    product.cost_price = spec["cost_price"]
                    product.selling_price = spec["selling_price"]
                    product.reorder_level = spec["reorder_level"]
                    product.is_active = True
                    await session.flush()
                    products_map[spec["sku"]] = product
                await session.commit()
                print("✓ Created sample products")

                cross_reference_pairs = [
                    ("SKF-6201", "NSK-6201"),
                    ("NSK-6201", "SKF-6201"),
                    ("SKF-6201", "NTN-6201"),
                    ("NTN-6201", "SKF-6201"),
                    ("NSK-6201", "NTN-6201"),
                    ("NTN-6201", "NSK-6201"),
                ]
                for product_sku, equivalent_sku in cross_reference_pairs:
                    existing_reference = await session.scalar(
                        select(ProductCrossReference).where(
                            ProductCrossReference.product_id == products_map[product_sku].id,
                            ProductCrossReference.equivalent_product_id == products_map[equivalent_sku].id,
                        )
                    )
                    if existing_reference is None:
                        session.add(
                            ProductCrossReference(
                                product_id=products_map[product_sku].id,
                                equivalent_product_id=products_map[equivalent_sku].id,
                                note="Equivalent bearing",
                            )
                        )
                await session.commit()
                print("✓ Created product cross references")

                initial_stock = {
                    "SKF-6201": 50,
                    "NSK-6201": 50,
                    "NTN-6201": 50,
                    "NGK-BP6ES": 100,
                    "NGK-CR8E": 100,
                    "BSH-OILF-01": 40,
                    "BRK-PAD-FRONT-01": 25,
                    "SUSP-FORK-OIL-10W": 20,
                    "BODY-MIRROR-L-01": 15,
                    "ELEC-BATT-12V7A": 10,
                }
                for sku, quantity in initial_stock.items():
                    existing_transaction = await session.scalar(
                        select(InventoryTransaction).where(
                            InventoryTransaction.product_id == products_map[sku].id,
                            InventoryTransaction.transaction_type == "adjustment",
                            InventoryTransaction.reference_type == "initial_seed",
                        )
                    )
                    if existing_transaction is None:
                        session.add(
                            InventoryTransaction(
                                product_id=products_map[sku].id,
                                transaction_type="adjustment",
                                quantity_change=quantity,
                                reference_id=None,
                                reference_type="initial_seed",
                                notes="Initial stock seeded",
                                created_by=admin_user.id,
                            )
                        )
                await session.commit()
                print("✓ Created initial stock transactions")
            except Exception:
                await session.rollback()
                raise

        print("🎉 Seed complete!")
    except Exception as exc:
        print(f"Error seeding database: {exc}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except Exception:
        raise SystemExit(1)
