from app.crud.project import (
    get_project_by_id,
    get_projects_by_team,
    create_project,
    update_project,
    delete_project,
)
from app.schemas.project import ProjectCreate, ProjectUpdate


def test_get_project_by_id_returns_project(db_session, project_obj):
    result = get_project_by_id(db_session, project_obj.id)
    assert result.id == project_obj.id


def test_get_project_by_id_returns_none_when_not_found(db_session):
    result = get_project_by_id(db_session, 999)

    assert result is None


def test_get_projects_by_team_returns_list(db_session, project_obj):
    result = get_projects_by_team(db_session, project_obj.team_id)
    assert len(result) == 1
    assert result[0].id == project_obj.id


def test_get_projects_by_team_returns_empty_list(db_session):
    result = get_projects_by_team(db_session, 999)

    assert result == []


def test_create_project(db_session, team_obj):
    team_id = team_obj.id
    project_data = ProjectCreate(name="Test project")

    result = create_project(db_session, team_id, project_data)

    assert result.name == project_data.name
    assert result.team_id == team_id
    assert result.id is not None


def test_create_project_sets_correct_team_id(db_session, team_obj):
    team_id = team_obj.id
    project_data = ProjectCreate(name="Test project")

    result = create_project(db_session, team_id, project_data)

    assert result.team_id == team_id


def test_update_project_updates_name(db_session, project_obj):
    update_data = ProjectUpdate(name="Updated name")

    result = update_project(db_session, project_obj, update_data)

    assert project_obj.name == "Updated name"
    assert result is project_obj


def test_update_project_only_provided_fields(db_session, project_obj):
    update_data = ProjectUpdate(name="Name")

    update_project(db_session, project_obj, update_data)

    updated_fields = update_data.model_dump(exclude_unset=True)
    assert "name" in updated_fields
    assert len(updated_fields) == 1


def test_update_project_empty_data(db_session, project_obj):
    update_data = ProjectUpdate()

    result = update_project(db_session, project_obj, update_data)

    assert result is project_obj


def test_delete_project_calls_delete_and_commit(db_session, project_obj):
    delete_project(db_session, project_obj)
    assert get_project_by_id(db_session, project_obj.id) is None


def test_delete_project_does_not_refresh(db_session, project_obj):
    delete_project(db_session, project_obj)
    assert get_projects_by_team(db_session, team_id=project_obj.team_id) == []
