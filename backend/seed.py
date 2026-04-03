"""
Seed script — populates the database with sample data.

Safe to run automatically on startup: skips seeding if the cafes table
already has rows, so it will never overwrite data created after first boot.

To force a re-seed (wipes all data): pass --force
    docker-compose exec backend python seed.py --force
"""

import asyncio
import sys
import uuid
import os
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/cafemanager",
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed(force: bool = False):
    # Import models after engine is set up
    from app.models import Cafe, Employee, CafeEmployee

    async with AsyncSessionLocal() as db:
        # ── Skip if data already exists (unless --force) ──────────────
        result = await db.execute(text("SELECT COUNT(*) FROM cafes"))
        count = result.scalar()
        if count > 0 and not force:
            print(f"✓ Database already has {count} cafe(s). Skipping seed. (Use --force to re-seed.)")
            return

        # ── Clear existing data (order matters due to FK constraints) ──
        await db.execute(text("DELETE FROM cafe_employees"))
        await db.execute(text("DELETE FROM employees"))
        await db.execute(text("DELETE FROM cafes"))
        await db.commit()

        # ── Cafes ──────────────────────────────────────────────────────
        cafe1 = Cafe(id=uuid.uuid4(), name="The Daily Grind", description="Artisan coffee and light bites in the heart of Orchard.", location="Orchard")
        cafe2 = Cafe(id=uuid.uuid4(), name="Brew & Co", description="Specialty brews with a stunning view of the bay.", location="Marina Bay")
        cafe3 = Cafe(id=uuid.uuid4(), name="Kopi Corner", description="Traditional Singapore kopi meets modern café culture.", location="Tampines")
        cafe4 = Cafe(id=uuid.uuid4(), name="Bean There", description="A cosy hideout for coffee lovers in the west.", location="Jurong")

        for cafe in [cafe1, cafe2, cafe3, cafe4]:
            db.add(cafe)
        await db.commit()

        # ── Employees ──────────────────────────────────────────────────
        emp1 = Employee(id="UIAB12345", name="Alice Tan", email_address="alice.tan@email.com", phone_number="91234567", gender="Female")
        emp2 = Employee(id="UIBC23456", name="Bob Lim", email_address="bob.lim@email.com", phone_number="81234567", gender="Male")
        emp3 = Employee(id="UICD34567", name="Clara Ng", email_address="clara.ng@email.com", phone_number="92345678", gender="Female")
        emp4 = Employee(id="UIDE45678", name="David Koh", email_address="david.koh@email.com", phone_number="83456789", gender="Male")
        emp5 = Employee(id="UIEF56789", name="Eva Wong", email_address="eva.wong@email.com", phone_number="94567890", gender="Female")
        emp6 = Employee(id="UIFG67890", name="Frank Lee", email_address="frank.lee@email.com", phone_number="85678901", gender="Male")
        emp7 = Employee(id="UIGH78901", name="Grace Chua", email_address="grace.chua@email.com", phone_number="96789012", gender="Female")
        emp8 = Employee(id="UIHI89012", name="Henry Goh", email_address="henry.goh@email.com", phone_number="87890123", gender="Male")

        for emp in [emp1, emp2, emp3, emp4, emp5, emp6, emp7, emp8]:
            db.add(emp)
        await db.commit()

        # ── Cafe Assignments (6 assigned, 2 unassigned) ────────────────
        today = date.today()
        assignments = [
            CafeEmployee(id=uuid.uuid4(), cafe_id=cafe1.id, employee_id=emp1.id, start_date=today - timedelta(days=365)),
            CafeEmployee(id=uuid.uuid4(), cafe_id=cafe1.id, employee_id=emp2.id, start_date=today - timedelta(days=200)),
            CafeEmployee(id=uuid.uuid4(), cafe_id=cafe2.id, employee_id=emp3.id, start_date=today - timedelta(days=150)),
            CafeEmployee(id=uuid.uuid4(), cafe_id=cafe2.id, employee_id=emp4.id, start_date=today - timedelta(days=90)),
            CafeEmployee(id=uuid.uuid4(), cafe_id=cafe3.id, employee_id=emp5.id, start_date=today - timedelta(days=500)),
            CafeEmployee(id=uuid.uuid4(), cafe_id=cafe4.id, employee_id=emp6.id, start_date=today - timedelta(days=30)),
            # emp7 and emp8 are unassigned
        ]
        for a in assignments:
            db.add(a)
        await db.commit()

        print("✓ Seed complete.")
        print(f"  Cafes: 4 ({cafe1.name}, {cafe2.name}, {cafe3.name}, {cafe4.name})")
        print(f"  Employees: 8 (6 assigned, 2 unassigned)")


if __name__ == "__main__":
    force = "--force" in sys.argv
    asyncio.run(seed(force=force))
