import re
from datetime import date, timedelta
from types import SimpleNamespace

from app.commands.employee_commands import _generate_employee_id, _to_response


def test_generate_employee_id_matches_required_format():
    for _ in range(20):
        employee_id = _generate_employee_id()
        assert re.fullmatch(r"UI[A-Z0-9]{7}", employee_id)
        assert len(employee_id) == 9


def test_employee_to_response_for_assigned_employee():
    start_date = date.today() - timedelta(days=15)
    employee = SimpleNamespace(
        id="UIAB12345",
        name="Alice Tan",
        email_address="alice@example.com",
        phone_number="91234567",
        gender="Female",
        assignment=SimpleNamespace(
            start_date=start_date,
            cafe=SimpleNamespace(name="Bean There"),
        ),
    )

    response = _to_response(employee)

    assert response.id == "UIAB12345"
    assert response.days_worked == 15
    assert response.cafe == "Bean There"


def test_employee_to_response_for_unassigned_employee():
    employee = SimpleNamespace(
        id="UIBC23456",
        name="Bob Lim",
        email_address="bob@example.com",
        phone_number="81234567",
        gender="Male",
        assignment=None,
    )

    response = _to_response(employee)

    assert response.id == "UIBC23456"
    assert response.days_worked == 0
    assert response.cafe == ""
