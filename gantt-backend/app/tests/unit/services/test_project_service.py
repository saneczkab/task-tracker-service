from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.services.project_service import (
    create_project_service,
    delete_project_service,
    get_team_projects_service,
    update_project_service,
)


@patch("app.services.project_service.project_crud.get_projects_by_team")
@patch("app.services.project_service.permissions.check_team_access")
def test_get_team_projects_service_success(
    mock_check_team_access, mock_get_projects_by_team, mock_db, ids
):
    expected_projects = [Mock(), Mock()]
    mock_get_projects_by_team.return_value = expected_projects

    result = get_team_projects_service(mock_db, ids.team_id, ids.user_id)

    mock_check_team_access.assert_called_once_with(mock_db, ids.team_id, ids.user_id)
    mock_get_projects_by_team.assert_called_once_with(mock_db, ids.team_id)
    assert result is expected_projects


@patch("app.services.project_service.project_crud.create_project")
@patch("app.services.project_service.permissions.check_team_access")
def test_create_project_service_success(
    mock_check_team_access, mock_create_project, mock_db, ids, mock_project
):
    project_data = Mock(name="Roadmap")
    mock_create_project.return_value = mock_project

    result = create_project_service(mock_db, ids.team_id, ids.user_id, project_data)

    mock_check_team_access.assert_called_once_with(
        mock_db, ids.team_id, ids.user_id, need_lead=True
    )
    mock_create_project.assert_called_once_with(mock_db, ids.team_id, project_data)
    assert result is mock_project


@patch("app.services.project_service.project_crud.update_project")
@patch("app.services.project_service.permissions.check_project_access")
def test_update_project_service_success(
    mock_check_project_access, mock_update_project, mock_db, ids, mock_project
):
    user_team = Mock()
    update_data = Mock(name="Updated")
    mock_check_project_access.return_value = (mock_project, user_team)
    mock_update_project.return_value = mock_project

    result = update_project_service(mock_db, ids.project_id, ids.user_id, update_data)

    mock_check_project_access.assert_called_once_with(
        mock_db, ids.project_id, ids.user_id, need_lead=True
    )
    mock_update_project.assert_called_once_with(mock_db, mock_project, update_data)
    assert result is mock_project


@patch("app.services.project_service.project_crud.delete_project_with_dependencies")
@patch("app.services.project_service.permissions.check_project_access")
def test_delete_project_service_success_with_streams(
    mock_check_project_access,
    mock_delete_project_with_dependencies,
    mock_db,
    ids,
    mock_project,
):
    mock_check_project_access.return_value = (mock_project, Mock())

    delete_project_service(mock_db, ids.project_id, ids.user_id)

    mock_delete_project_with_dependencies.assert_called_once_with(
        mock_db, ids.project_id
    )


@patch("app.services.project_service.project_crud.delete_project_with_dependencies")
@patch("app.services.project_service.permissions.check_project_access")
def test_delete_project_service_propagates_access_error(
    mock_check_project_access, mock_delete_project_with_dependencies, mock_db, ids
):
    mock_check_project_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_project_service(mock_db, ids.project_id, ids.user_id)

    mock_delete_project_with_dependencies.assert_not_called()
