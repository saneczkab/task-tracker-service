import pytest
from pydantic import ValidationError

from app.schemas.calendar import CalendarExport


def test_calendar_export_valid_enums():
    result = CalendarExport(scope="all", target="all")
    assert result.scope.value == "all"
    assert result.target.value == "all"


def test_calendar_export_invalid_scope():
    with pytest.raises(ValidationError):
        CalendarExport(scope="invalid", target="all")


def test_calendar_export_invalid_target():
    with pytest.raises(ValidationError):
        CalendarExport(scope="all", target="invalid")
