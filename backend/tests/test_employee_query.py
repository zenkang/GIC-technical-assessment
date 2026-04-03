from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.queries.employee_queries import GetEmployeesQuery


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return list(self._values)


class _ExecuteResult:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return _ScalarResult(self._values)


def _employee(employee_id: str, days_worked: int, cafe_name: str | None):
    assignment = None
    if days_worked > 0:
        assignment = SimpleNamespace(
            start_date=date.today() - timedelta(days=days_worked),
            cafe=SimpleNamespace(name=cafe_name) if cafe_name else None,
        )

    return SimpleNamespace(
        id=employee_id,
        name=f"Name {employee_id}",
        email_address=f"{employee_id.lower()}@example.com",
        phone_number="91234567",
        gender="Male",
        assignment=assignment,
    )


@pytest.mark.asyncio
async def test_get_employees_query_sorts_by_days_worked_descending():
    employees = [
        _employee("UICD34567", 3, "Kopi Corner"),
        _employee("UIAB12345", 20, "Bean There"),
        _employee("UIEF56789", 0, None),
    ]

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_ExecuteResult(employees))

    responses = await GetEmployeesQuery().execute(db)

    assert [r.id for r in responses] == ["UIAB12345", "UICD34567", "UIEF56789"]
    assert [r.days_worked for r in responses] == [20, 3, 0]


@pytest.mark.asyncio
async def test_get_employees_query_handles_unassigned_employee_values():
    employees = [_employee("UIGH78901", 0, None)]

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_ExecuteResult(employees))

    responses = await GetEmployeesQuery().execute(db)

    assert len(responses) == 1
    assert responses[0].id == "UIGH78901"
    assert responses[0].days_worked == 0
    assert responses[0].cafe == ""
