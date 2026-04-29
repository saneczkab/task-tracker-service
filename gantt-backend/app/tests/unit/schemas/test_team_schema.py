import pytest
from pydantic import ValidationError

from app.schemas.team import TeamCreate, TeamUpdate


def test_team_create_non_empty_name():
    result = TeamCreate(name="Team")
    assert result.name == "Team"


def test_team_create_empty_name():
    with pytest.raises(ValidationError):
        TeamCreate(name="")


def test_team_update_empty_payload():
    result = TeamUpdate()
    assert result.name is None
    assert result.newUsers is None
    assert result.deleteUsers is None


def test_team_update_empty_name():
    with pytest.raises(ValidationError):
        TeamUpdate(name="")


def test_team_update_invalid_email_in_new_users():
    with pytest.raises(ValidationError):
        TeamUpdate(newUsers=["not-an-email"])
