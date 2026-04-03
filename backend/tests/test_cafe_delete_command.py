import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.commands.cafe_commands import DeleteCafeCommand


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return list(self._values)


class _ExecuteResult:
    def __init__(self, one=None, many=None):
        self._one = one
        self._many = many or []

    def scalar_one_or_none(self):
        return self._one

    def scalars(self):
        return _ScalarResult(self._many)


@pytest.mark.asyncio
async def test_delete_cafe_removes_cafe_and_assigned_employees():
    cafe_id = uuid.uuid4()
    employee_ids = ["UIAB12345", "UIBC23456"]

    cafe = SimpleNamespace(id=cafe_id, logo=None)
    employees = [SimpleNamespace(id=employee_ids[0]), SimpleNamespace(id=employee_ids[1])]

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _ExecuteResult(one=cafe),
            _ExecuteResult(many=employee_ids),
            _ExecuteResult(many=employees),
        ]
    )
    db.delete = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    command = DeleteCafeCommand(cafe_id=cafe_id)
    result = await command.execute(db)

    assert result == {"detail": "Cafe deleted"}
    assert db.delete.await_count == 3

    deleted_objects = [call.args[0] for call in db.delete.await_args_list]
    assert cafe in deleted_objects
    assert employees[0] in deleted_objects
    assert employees[1] in deleted_objects

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_cafe_raises_when_not_found():
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[_ExecuteResult(one=None)])

    command = DeleteCafeCommand(cafe_id=uuid.uuid4())

    with pytest.raises(HTTPException) as exc_info:
        await command.execute(db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Cafe not found"


@pytest.mark.asyncio
async def test_delete_cafe_with_no_assignments_skips_employee_deletes():
    cafe_id = uuid.uuid4()
    cafe = SimpleNamespace(id=cafe_id, logo=None)

    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _ExecuteResult(one=cafe),
            _ExecuteResult(many=[]),
        ]
    )
    db.delete = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    command = DeleteCafeCommand(cafe_id=cafe_id)
    result = await command.execute(db)

    assert result == {"detail": "Cafe deleted"}
    assert db.delete.await_count == 1
    assert db.delete.await_args_list[0].args[0] is cafe
    assert db.execute.await_count == 2
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
