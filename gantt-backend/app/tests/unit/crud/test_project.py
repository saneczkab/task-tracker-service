from unittest.mock import Mock

from app.crud.project import (
    get_project_by_id,
    get_projects_by_team,
    create_project,
    update_project,
    delete_project,
)
from app.schemas.project import ProjectCreate, ProjectUpdate


def test_get_project_by_id_returns_project():
    mock_db = Mock()
    project_id = 42
    expected_project = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected_project

    result = get_project_by_id(mock_db, project_id)

    assert result is expected_project
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_project_by_id_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_project_by_id(mock_db, 999)

    assert result is None


def test_get_projects_by_team_returns_list():
    mock_db = Mock()
    team_id = 42
    expected_projects = [Mock(), Mock()]
    mock_db.query.return_value.filter.return_value.all.return_value = expected_projects

    result = get_projects_by_team(mock_db, team_id)

    assert result == expected_projects
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_projects_by_team_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_projects_by_team(mock_db, 999)

    assert result == []


def test_create_project():
    mock_db = Mock()
    team_id = 42
    project_data = ProjectCreate(name="Test project")

    result = create_project(mock_db, team_id, project_data)

    assert result.name == project_data.name
    assert result.team_id == team_id

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


def test_create_project_sets_correct_team_id():
    mock_db = Mock()
    team_id = 42
    project_data = ProjectCreate(name="Test project")

    result = create_project(mock_db, team_id, project_data)

    assert result.team_id == team_id


def test_update_project_updates_name():
    mock_db = Mock()
    project_obj = Mock()
    update_data = ProjectUpdate(name="Updated name")

    result = update_project(mock_db, project_obj, update_data)

    assert project_obj.name == "Updated name"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(project_obj)
    assert result is project_obj


def test_update_project_only_provided_fields():
    mock_db = Mock()
    project_obj = Mock()
    update_data = ProjectUpdate(name="Name")

    update_project(mock_db, project_obj, update_data)

    updated_fields = update_data.model_dump(exclude_unset=True)
    assert "name" in updated_fields
    assert len(updated_fields) == 1


def test_update_project_empty_data():
    mock_db = Mock()
    project_obj = Mock()
    update_data = ProjectUpdate()

    result = update_project(mock_db, project_obj, update_data)

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(project_obj)
    assert result is project_obj


def test_delete_project_calls_delete_and_commit():
    mock_db = Mock()
    project_obj = Mock()

    delete_project(mock_db, project_obj)

    mock_db.delete.assert_called_once_with(project_obj)
    mock_db.commit.assert_called_once()


def test_delete_project_does_not_refresh():
    mock_db = Mock()
    project_obj = Mock()

    delete_project(mock_db, project_obj)

    mock_db.refresh.assert_not_called()
