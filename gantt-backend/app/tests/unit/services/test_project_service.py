from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.models import goal as goal_model
from app.models import stream as stream_model
from app.models import task as task_model
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


@patch("app.services.project_service.project_crud.delete_project")
@patch("app.services.project_service.permissions.check_project_access")
def test_delete_project_service_success_with_streams(
    mock_check_project_access,
    mock_delete_project,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_project,
    mock_stream,
):
    mock_check_project_access.return_value = (mock_project, Mock())

    q_streams_all = make_query(all_=[mock_stream])
    q_task_delete = make_query()
    q_goal_delete = make_query()
    q_streams_delete = make_query()

    mock_db.query.side_effect = make_query_router(
        {
            stream_model.Stream: [q_streams_all, q_streams_delete],
            task_model.Task: q_task_delete,
            goal_model.Goal: q_goal_delete,
        }
    )

    delete_project_service(mock_db, ids.project_id, ids.user_id)

    mock_delete_project.assert_called_once_with(mock_db, mock_project)


@patch("app.services.project_service.project_crud.delete_project")
@patch("app.services.project_service.permissions.check_project_access")
def test_delete_project_service_propagates_access_error(
    mock_check_project_access, mock_delete_project, mock_db, ids
):
    mock_check_project_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_project_service(mock_db, ids.project_id, ids.user_id)

    mock_delete_project.assert_not_called()
