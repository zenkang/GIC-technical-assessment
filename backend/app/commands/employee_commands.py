"""
CQRS Write Commands for Employee resources.

Employee IDs are auto-generated as "UI" + 7 random alphanumeric characters.
The cafe assignment relationship is managed here: creating/updating/removing
the CafeEmployee junction record as needed.
"""

import random
import string
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Employee, CafeEmployee, Cafe
from app.schemas import EmployeeResponse


def _generate_employee_id() -> str:
    #Generate a unique employee ID: UI + 7 random alphanumeric characters.
    chars = string.ascii_uppercase + string.digits
    return "UI" + "".join(random.choices(chars, k=7))


def _to_response(employee: Employee) -> EmployeeResponse:
    #Build an EmployeeResponse from an ORM Employee (with loaded assignment).
    assignment = employee.assignment
    days_worked = 0
    cafe_name = ""
    if assignment:
        days_worked = (date.today() - assignment.start_date).days
        cafe_name = assignment.cafe.name if assignment.cafe else ""

    return EmployeeResponse(
        id=employee.id,
        name=employee.name,
        email_address=employee.email_address,
        phone_number=employee.phone_number,
        gender=employee.gender,
        days_worked=days_worked,
        cafe=cafe_name,
    )


@dataclass
class CreateEmployeeCommand:
    name: str
    email_address: str
    phone_number: str
    gender: str
    cafe_id: Optional[uuid.UUID]

    async def execute(self, db: AsyncSession) -> EmployeeResponse:
        # Generate a unique employee ID(tries 10 times)
        for _ in range(10):
            emp_id = _generate_employee_id()
            existing = await db.get(Employee, emp_id)
            if not existing:
                break
        else:
            raise HTTPException(status_code=500, detail="Failed to generate unique employee ID")

        employee = Employee(
            id=emp_id,
            name=self.name,
            email_address=self.email_address,
            phone_number=self.phone_number,
            gender=self.gender,
        )
        db.add(employee)

        if self.cafe_id:
            # Verify the cafe exists
            cafe = await db.get(Cafe, self.cafe_id)
            if not cafe:
                raise HTTPException(status_code=404, detail="Cafe not found")
            assignment = CafeEmployee(
                id=uuid.uuid4(),
                cafe_id=self.cafe_id,
                employee_id=emp_id,
                start_date=date.today(),
            )
            db.add(assignment)

        await db.commit()

        # Reload with relationships
        result = await db.execute(
            select(Employee)
            .where(Employee.id == emp_id)
            .options(
                selectinload(Employee.assignment).selectinload(CafeEmployee.cafe)
            )
        )
        employee = result.scalar_one()
        return _to_response(employee)


@dataclass
class UpdateEmployeeCommand:
    employee_id: str
    name: str
    email_address: str
    phone_number: str
    gender: str
    cafe_id: Optional[uuid.UUID]

    async def execute(self, db: AsyncSession) -> EmployeeResponse:
        result = await db.execute(
            select(Employee)
            .where(Employee.id == self.employee_id)
            .options(selectinload(Employee.assignment).selectinload(CafeEmployee.cafe))
        )
        employee = result.scalar_one_or_none()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Update scalar fields
        employee.name = self.name
        employee.email_address = self.email_address
        employee.phone_number = self.phone_number
        employee.gender = self.gender

        current_assignment = employee.assignment

        if self.cafe_id is None:
            # Remove assignment if one exists
            if current_assignment:
                await db.delete(current_assignment)
        else:
            # Verify cafe exists
            cafe = await db.get(Cafe, self.cafe_id)
            if not cafe:
                raise HTTPException(status_code=404, detail="Cafe not found")

            if current_assignment:
                if current_assignment.cafe_id == self.cafe_id:
                    # Same cafe — keep existing start_date, no change needed
                    pass
                else:
                    # Different cafe — delete old assignment, create new one
                    await db.delete(current_assignment)
                    await db.flush()
                    new_assignment = CafeEmployee(
                        id=uuid.uuid4(),
                        cafe_id=self.cafe_id,
                        employee_id=self.employee_id,
                        start_date=date.today(),
                    )
                    db.add(new_assignment)
            else:
                # No previous assignment — create one
                new_assignment = CafeEmployee(
                    id=uuid.uuid4(),
                    cafe_id=self.cafe_id,
                    employee_id=self.employee_id,
                    start_date=date.today(),
                )
                db.add(new_assignment)

        await db.commit()

        # Reload with fresh relationships
        result = await db.execute(
            select(Employee)
            .where(Employee.id == self.employee_id)
            .options(selectinload(Employee.assignment).selectinload(CafeEmployee.cafe))
        )
        employee = result.scalar_one()
        return _to_response(employee)


@dataclass
class DeleteEmployeeCommand:
    employee_id: str

    async def execute(self, db: AsyncSession) -> dict:
        employee = await db.get(Employee, self.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # cascade="all, delete-orphan" on Employee.assignment handles the CafeEmployee row
        await db.delete(employee)
        await db.commit()
        return {"detail": "Employee deleted"}
