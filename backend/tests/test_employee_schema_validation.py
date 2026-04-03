import uuid

import pytest
from pydantic import ValidationError

from app.schemas.employee import EmployeeCreate


def _valid_payload():
    return {
        "name": "Alice Tan",
        "email_address": "alice@example.com",
        "phone_number": "91234567",
        "gender": "Female",
        "cafe_id": uuid.uuid4(),
    }


def test_employee_create_accepts_valid_payload():
    payload = EmployeeCreate(**_valid_payload())
    assert payload.phone_number == "91234567"
    assert payload.gender == "Female"


def test_employee_create_rejects_invalid_phone():
    invalid = _valid_payload()
    invalid["phone_number"] = "71234567"

    with pytest.raises(ValidationError) as exc_info:
        EmployeeCreate(**invalid)

    assert "Phone number must start with 8 or 9 and be exactly 8 digits" in str(exc_info.value)


def test_employee_create_rejects_invalid_gender():
    invalid = _valid_payload()
    invalid["gender"] = "Other"

    with pytest.raises(ValidationError) as exc_info:
        EmployeeCreate(**invalid)

    assert "Gender must be Male or Female" in str(exc_info.value)
