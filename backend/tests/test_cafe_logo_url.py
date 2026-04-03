import uuid
from types import SimpleNamespace

from app.commands.cafe_commands import _to_response


def test_cafe_response_uses_relative_logo_url():
    cafe = SimpleNamespace(
        id=uuid.uuid4(),
        name="Bean There",
        description="A cozy coffee place",
        logo="logo.png",
        location="Jurong",
    )

    response = _to_response(cafe, employee_count=3)

    assert response.logo == "/static/logos/logo.png"


def test_cafe_response_without_logo_sets_none():
    cafe = SimpleNamespace(
        id=uuid.uuid4(),
        name="Bean There",
        description="A cozy coffee place",
        logo=None,
        location="Jurong",
    )

    response = _to_response(cafe, employee_count=0)

    assert response.logo is None
