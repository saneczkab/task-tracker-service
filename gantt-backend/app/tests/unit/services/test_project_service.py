from unittest.mock import Mock, patch
import pytest

from app.core import exception
from app.models.role import Role
from app.services.project_service import (
    get_team_projects_service,
    create_project_service,
    update_project_service,
    delete_project_service,
    check_team_permissions,
)


def test_check_team_permissions_success():
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    user_team = Mock(role_id=Role.READER)

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        team_obj,
        user_team,
    ]

    result = check_team_permissions(mock_db, team_id, user_id)

    assert result is user_team


def test_check_team_permissions_need_lead_success():
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    user_team = Mock(role_id=Role.EDITOR)

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        team_obj,
        user_team,
    ]

    result = check_team_permissions(mock_db, team_id, user_id, need_lead=True)

    assert result is user_team


def test_check_team_permissions_team_not_found():
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        check_team_permissions(mock_db, team_id, user_id)


def test_check_team_permissions_user_not_in_team():
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)

    mock_db.query.return_value.filter.return_value.first.side_effect = [team_obj, None]

    with pytest.raises(exception.ForbiddenError):
        check_team_permissions(mock_db, team_id, user_id)


def test_check_team_permissions_need_lead_but_not_editor():
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    user_team = Mock(role_id=Role.READER)

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        team_obj,
        user_team,
    ]

    with pytest.raises(exception.ForbiddenError):
        check_team_permissions(mock_db, team_id, user_id, need_lead=True)


@patch("app.services.project_service.check_team_permissions")
@patch("app.services.project_service.project_crud.get_projects_by_team")
def test_get_team_projects_service_success(mock_get_projects, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    mock_projects = [Mock(), Mock()]

    mock_check_perms.return_value = Mock(id=team_id)
    mock_get_projects.return_value = mock_projects

    result = get_team_projects_service(mock_db, team_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, team_id, user_id)
    mock_get_projects.assert_called_once_with(mock_db, team_id)
    assert result == mock_projects


@patch("app.services.project_service.check_team_permissions")
@patch("app.services.project_service.project_crud.get_projects_by_team")
def test_get_team_projects_service_forbidden(mock_get_projects, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_team_projects_service(mock_db, team_id, user_id)

    mock_get_projects.assert_not_called()


@patch("app.services.project_service.check_team_permissions")
@patch("app.services.project_service.project_crud.get_projects_by_team")
def test_get_team_projects_service_team_not_found(mock_get_projects, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_team_projects_service(mock_db, team_id, user_id)

    mock_get_projects.assert_not_called()


@patch("app.services.project_service.check_team_permissions")
@patch("app.services.project_service.project_crud.create_project")
def test_create_project_service_success(mock_create, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    project_data = Mock()
    project_data.name = "Test project"

    mock_check_perms.return_value = Mock(id=team_id)
    expected_project = Mock()
    mock_create.return_value = expected_project

    result = create_project_service(mock_db, team_id, user_id, project_data)

    mock_check_perms.assert_called_once_with(mock_db, team_id, user_id, need_lead=True)
    mock_create.assert_called_once_with(mock_db, team_id, project_data)
    assert result is expected_project


@patch("app.services.project_service.check_team_permissions")
@patch("app.services.project_service.project_crud.create_project")
def test_create_project_service_forbidden(mock_create, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    project_data = Mock()
    project_data.name = "Test project"

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        create_project_service(mock_db, team_id, user_id, project_data)

    mock_create.assert_not_called()


@patch("app.services.project_service.check_team_permissions")
@patch("app.services.project_service.project_crud.create_project")
def test_create_project_service_team_not_found(mock_create, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    project_data = Mock()
    project_data.name = "Test project"

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        create_project_service(mock_db, team_id, user_id, project_data)

    mock_create.assert_not_called()


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.update_project")
def test_update_project_service_success(mock_update, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42
    project_obj = Mock(id=proj_id)
    update_data = Mock()
    update_data.name = "Test project"

    mock_check_perms.return_value = project_obj
    expected = Mock()
    mock_update.return_value = expected

    result = update_project_service(mock_db, proj_id, user_id, update_data)

    mock_check_perms.assert_called_once_with(mock_db, proj_id, user_id, need_lead=True)
    mock_update.assert_called_once_with(mock_db, project_obj, update_data)
    assert result is expected


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.update_project")
def test_update_project_service_project_not_found(mock_update, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42
    update_data = Mock()
    update_data.name = "Test project"

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        update_project_service(mock_db, proj_id, user_id, update_data)

    mock_update.assert_not_called()


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.update_project")
def test_update_project_service_forbidden(mock_update, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42
    update_data = Mock()
    update_data.name = "Test project"

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        update_project_service(mock_db, proj_id, user_id, update_data)

    mock_update.assert_not_called()


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.delete_project")
def test_delete_project_service_success_no_streams(mock_delete, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42
    project_obj = Mock(id=proj_id)

    mock_check_perms.return_value = project_obj
    mock_db.query.return_value.filter.return_value.all.return_value = []

    delete_project_service(mock_db, proj_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, proj_id, user_id, need_lead=True)
    mock_delete.assert_called_once_with(mock_db, project_obj)


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.delete_project")
def test_delete_project_service_success_with_streams(mock_delete, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42
    project_obj = Mock(id=proj_id)
    stream1 = Mock(id=42)
    stream2 = Mock(id=43)

    mock_check_perms.return_value = project_obj
    mock_db.query.return_value.filter.return_value.all.return_value = [stream1, stream2]
    mock_db.query.return_value.filter.return_value.delete.return_value = None

    delete_project_service(mock_db, proj_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, proj_id, user_id, need_lead=True)
    mock_delete.assert_called_once_with(mock_db, project_obj)


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.delete_project")
def test_delete_project_service_project_not_found(mock_delete, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        delete_project_service(mock_db, proj_id, user_id)

    mock_delete.assert_not_called()


@patch("app.services.project_service.check_project_permissions")
@patch("app.services.project_service.project_crud.delete_project")
def test_delete_project_service_forbidden(mock_delete, mock_check_perms):
    mock_db = Mock()
    proj_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_project_service(mock_db, proj_id, user_id)

    mock_delete.assert_not_called()
