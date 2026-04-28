import pytest
from pydantic import ValidationError

from app.schemas.project import ProjectCreate, ProjectUpdate


def test_project_create_non_empty_name():
    result = ProjectCreate(name="Project")
    assert result.name == "Project"


def test_project_create_empty_name():
    with pytest.raises(ValidationError):
        ProjectCreate(name="")


def test_project_update_empty_payload():
    result = ProjectUpdate()
    assert result.name is None


def test_project_update_empty_name():
    with pytest.raises(ValidationError):
        ProjectUpdate(name="")
