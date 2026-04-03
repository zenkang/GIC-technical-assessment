"""
CQRS Write Commands for Cafe resources.

Each command encapsulates a single write operation. The execute() method
receives an AsyncSession and returns the result. Route handlers never
access the DB directly — they call mediator.send(SomeCommand(...)).
"""

import uuid
import os
import shutil
from dataclasses import dataclass, field
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Cafe
from app.schemas import CafeResponse

LOGO_DIR = "/app/static/logos"
MAX_LOGO_BYTES = 2 * 1024 * 1024  # 2 MB


async def _save_logo(logo: UploadFile) -> str:
    #Save uploaded logo file to disk, return the stored filename.
    os.makedirs(LOGO_DIR, exist_ok=True)
    contents = await logo.read()
    if len(contents) > MAX_LOGO_BYTES:
        raise HTTPException(status_code=400, detail="Logo file must be 2 MB or smaller")
    ext = os.path.splitext(logo.filename or "")[1] or ".png"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(LOGO_DIR, filename)
    with open(path, "wb") as f:
        f.write(contents)
    return filename


def _to_response(cafe: Cafe, employee_count: int) -> CafeResponse:
    logo_url = f"/static/logos/{cafe.logo}" if cafe.logo else None
    return CafeResponse(
        id=cafe.id,
        name=cafe.name,
        description=cafe.description,
        employees=employee_count,
        logo=logo_url,
        location=cafe.location,
    )


@dataclass
class CreateCafeCommand:
    name: str
    description: str
    location: str
    logo: Optional[UploadFile] = field(default=None)

    async def execute(self, db: AsyncSession) -> CafeResponse:
        logo_filename = None
        if self.logo and self.logo.filename:
            logo_filename = await _save_logo(self.logo)

        cafe = Cafe(
            id=uuid.uuid4(),
            name=self.name,
            description=self.description,
            location=self.location,
            logo=logo_filename,
        )
        db.add(cafe)
        await db.commit()
        await db.refresh(cafe)
        return _to_response(cafe, 0)


@dataclass
class UpdateCafeCommand:
    cafe_id: uuid.UUID
    name: str
    description: str
    location: str
    logo: Optional[UploadFile] = field(default=None)

    async def execute(self, db: AsyncSession) -> CafeResponse:
        result = await db.execute(select(Cafe).where(Cafe.id == self.cafe_id))
        cafe = result.scalar_one_or_none()
        if not cafe:
            raise HTTPException(status_code=404, detail="Cafe not found")

        # If a new logo is uploaded, replace the old file
        if self.logo and self.logo.filename:
            if cafe.logo:
                old_path = os.path.join(LOGO_DIR, cafe.logo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            cafe.logo = await _save_logo(self.logo)

        cafe.name = self.name
        cafe.description = self.description
        cafe.location = self.location

        await db.commit()
        await db.refresh(cafe)

        # Count current employees
        from app.models import CafeEmployee
        count_result = await db.execute(
            select(CafeEmployee).where(CafeEmployee.cafe_id == cafe.id)
        )
        count = len(count_result.scalars().all())
        return _to_response(cafe, count)


@dataclass
class DeleteCafeCommand:
    cafe_id: uuid.UUID

    async def execute(self, db: AsyncSession) -> dict:
        from app.models import CafeEmployee, Employee

        result = await db.execute(select(Cafe).where(Cafe.id == self.cafe_id))
        cafe = result.scalar_one_or_none()
        if not cafe:
            raise HTTPException(status_code=404, detail="Cafe not found")

        # Collect employee IDs assigned to this cafe before deleting
        assignment_result = await db.execute(
            select(CafeEmployee.employee_id).where(CafeEmployee.cafe_id == self.cafe_id)
        )
        employee_ids = assignment_result.scalars().all()

        # Remove logo file if it exists
        if cafe.logo:
            logo_path = os.path.join(LOGO_DIR, cafe.logo)
            if os.path.exists(logo_path):
                os.remove(logo_path)

        # Delete the cafe (cascade deletes cafe_employees assignments)
        await db.delete(cafe)
        await db.flush()

        # Delete the employees that were assigned to this cafe
        if employee_ids:
            emp_result = await db.execute(
                select(Employee).where(Employee.id.in_(employee_ids))
            )
            for emp in emp_result.scalars().all():
                await db.delete(emp)

        await db.commit()
        return {"detail": "Cafe deleted"}
