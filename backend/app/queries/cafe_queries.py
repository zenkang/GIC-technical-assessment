"""
CQRS Read Queries for Cafe resources.

Queries are pure reads — they never modify state. They return
fully-formed response objects that route handlers can return directly.
"""

from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Cafe, CafeEmployee
from app.schemas import CafeResponse


@dataclass
class GetCafesQuery:
    location: Optional[str] = None  # if provided, filter by this location (case-insensitive)

    async def execute(self, db: AsyncSession) -> List[CafeResponse]:
        # Sub-query: count employees per cafe
        employee_count_subq = (
            select(
                CafeEmployee.cafe_id,
                func.count(CafeEmployee.employee_id).label("emp_count"),
            )
            .group_by(CafeEmployee.cafe_id)
            .subquery()
        )

        query = (
            select(
                Cafe,
                func.coalesce(employee_count_subq.c.emp_count, 0).label("emp_count"),
            )
            .outerjoin(employee_count_subq, Cafe.id == employee_count_subq.c.cafe_id)
            .order_by(func.coalesce(employee_count_subq.c.emp_count, 0).desc())
        )

        if self.location:
            query = query.where(func.lower(Cafe.location) == self.location.lower())

        result = await db.execute(query)
        rows = result.all()

        responses = []
        for row in rows:
            cafe: Cafe = row[0]
            emp_count: int = row[1]
            logo_url = f"/static/logos/{cafe.logo}" if cafe.logo else None
            responses.append(
                CafeResponse(
                    id=cafe.id,
                    name=cafe.name,
                    description=cafe.description,
                    employees=emp_count,
                    logo=logo_url,
                    location=cafe.location,
                )
            )

        return responses
