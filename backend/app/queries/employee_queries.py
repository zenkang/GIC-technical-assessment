"""
CQRS Read Queries for Employee resources.

days_worked is computed as (today - start_date).days.
Employees not assigned to any cafe have days_worked=0 and cafe="".
Results are sorted by days_worked descending.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Employee, CafeEmployee, Cafe
from app.schemas import EmployeeResponse


@dataclass
class GetEmployeesQuery:
    cafe: Optional[str] = None  # filter by cafe name (case-insensitive)

    async def execute(self, db: AsyncSession) -> List[EmployeeResponse]:
        query = (
            select(Employee)
            .options(
                selectinload(Employee.assignment).selectinload(CafeEmployee.cafe)
            )
        )

        if self.cafe:
            # Filter: only employees whose assignment's cafe name matches
            query = (
                query
                .join(Employee.assignment)
                .join(CafeEmployee.cafe)
                .where(func_lower_cafe(Cafe.name) == self.cafe.lower())
            )

        result = await db.execute(query)
        employees = result.scalars().all()

        today = date.today()
        responses = []
        for emp in employees:
            assignment = emp.assignment
            days_worked = 0
            cafe_name = ""
            if assignment:
                days_worked = (today - assignment.start_date).days
                cafe_name = assignment.cafe.name if assignment.cafe else ""

            responses.append(
                EmployeeResponse(
                    id=emp.id,
                    name=emp.name,
                    email_address=emp.email_address,
                    phone_number=emp.phone_number,
                    gender=emp.gender,
                    days_worked=days_worked,
                    cafe=cafe_name,
                )
            )

        # Sort by days_worked descending in Python (avoids a complex SQL expression)
        responses.sort(key=lambda r: r.days_worked, reverse=True)
        return responses


def func_lower_cafe(column):
    """Helper: apply SQL lower() to a column for case-insensitive comparison."""
    from sqlalchemy import func
    return func.lower(column)
