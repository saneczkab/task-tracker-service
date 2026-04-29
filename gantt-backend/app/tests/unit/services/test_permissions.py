from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.models.role import Role
from app.models import team as team_model
from app.services.permissions import (
    check_editor_permission,
    check_project_access,
    check_stream_access,
    check_task_access,
    check_team_access,
)


def test_check_team_access_not_found(mock_db, ids, make_query):
    q_team = make_query(first=None)
    mock_db.query.side_effect = lambda model: q_team

    with pytest.raises(exception.NotFoundError, match="Команда не найдена"):
        check_team_access(mock_db, ids.team_id, ids.user_id)

    mock_db.query.assert_called_once()


def test_check_team_access_forbidden_without_membership(
    mock_db, ids, make_query_router, make_query, mock_team
):
    mock_db.query.side_effect = make_query_router(
        {
            team_model.Team: make_query(first=mock_team),
            team_model.UserTeam: make_query(first=None),
        }
    )

    with pytest.raises(
        exception.ForbiddenError, match="У вас нет доступа к этой команде"
    ):
        check_team_access(mock_db, ids.team_id, ids.user_id)


def test_check_team_access_forbidden_need_lead(
    mock_db, ids, make_query_router, make_query, mock_team
):
    user_team = Mock(role_id=Role.READER)
    mock_db.query.side_effect = make_query_router(
        {
            team_model.Team: make_query(first=mock_team),
            team_model.UserTeam: make_query(first=user_team),
        }
    )

    with pytest.raises(
        exception.ForbiddenError, match="У вас нет прав на выполнение этого действия"
    ):
        check_team_access(mock_db, ids.team_id, ids.user_id, need_lead=True)


def test_check_team_access_success(
    mock_db, ids, make_query_router, make_query, mock_team
):
    user_team = Mock(role_id=Role.EDITOR)
    mock_db.query.side_effect = make_query_router(
        {
            team_model.Team: make_query(first=mock_team),
            team_model.UserTeam: make_query(first=user_team),
        }
    )

    result_team, result_user_team = check_team_access(
        mock_db, ids.team_id, ids.user_id, need_lead=True
    )

    assert result_team is mock_team
    assert result_user_team is user_team


@patch("app.services.permissions.project_crud.get_project_by_id")
def test_check_project_access_not_found(mock_get_project_by_id, mock_db, ids):
    mock_get_project_by_id.return_value = None

    with pytest.raises(exception.NotFoundError, match="Проект не найден"):
        check_project_access(mock_db, ids.project_id, ids.user_id)

    mock_db.query.assert_not_called()


@patch("app.services.permissions.project_crud.get_project_by_id")
def test_check_project_access_forbidden_without_membership(
    mock_get_project_by_id, mock_db, ids, make_query, mock_project
):
    mock_get_project_by_id.return_value = mock_project
    mock_db.query.return_value = make_query(first=None)

    with pytest.raises(
        exception.ForbiddenError, match="Вы должны состоять в команде проекта"
    ):
        check_project_access(mock_db, ids.project_id, ids.user_id)


@patch("app.services.permissions.project_crud.get_project_by_id")
def test_check_project_access_forbidden_need_lead(
    mock_get_project_by_id, mock_db, ids, make_query, mock_project
):
    user_team = Mock(role_id=Role.READER)
    mock_get_project_by_id.return_value = mock_project
    mock_db.query.return_value = make_query(first=user_team)

    with pytest.raises(
        exception.ForbiddenError, match="У вас нет прав на выполнение этого действия"
    ):
        check_project_access(mock_db, ids.project_id, ids.user_id, need_lead=True)


@patch("app.services.permissions.project_crud.get_project_by_id")
def test_check_project_access_success(
    mock_get_project_by_id, mock_db, ids, make_query, mock_project
):
    user_team = Mock(role_id=Role.EDITOR)
    mock_get_project_by_id.return_value = mock_project
    mock_db.query.return_value = make_query(first=user_team)

    result_project, result_user_team = check_project_access(
        mock_db, ids.project_id, ids.user_id, need_lead=True
    )

    assert result_project is mock_project
    assert result_user_team is user_team


@patch("app.services.permissions.check_project_access")
@patch("app.services.permissions.stream_crud.get_stream_by_id")
def test_check_stream_access_not_found(
    mock_get_stream_by_id, mock_check_project_access, mock_db, ids
):
    mock_get_stream_by_id.return_value = None

    with pytest.raises(exception.NotFoundError, match="Стрим не найден"):
        check_stream_access(mock_db, ids.stream_id, ids.user_id)

    mock_check_project_access.assert_not_called()


@patch("app.services.permissions.check_project_access")
@patch("app.services.permissions.stream_crud.get_stream_by_id")
def test_check_stream_access_success(
    mock_get_stream_by_id,
    mock_check_project_access,
    mock_db,
    ids,
    mock_stream,
    mock_project,
):
    user_team = Mock(role_id=Role.EDITOR)
    mock_get_stream_by_id.return_value = mock_stream
    mock_check_project_access.return_value = (mock_project, user_team)

    result_stream, result_project, result_user_team = check_stream_access(
        mock_db, ids.stream_id, ids.user_id, need_lead=True
    )

    mock_check_project_access.assert_called_once_with(
        mock_db, ids.project_id, ids.user_id, need_lead=True
    )
    assert result_stream is mock_stream
    assert result_project is mock_project
    assert result_user_team is user_team


@patch("app.services.permissions.check_stream_access")
@patch("app.services.permissions.task_crud.get_task_by_id")
def test_check_task_access_not_found(
    mock_get_task_by_id, mock_check_stream_access, mock_db, ids
):
    mock_get_task_by_id.return_value = None

    with pytest.raises(exception.NotFoundError, match="Задача не найдена"):
        check_task_access(mock_db, ids.task_id, ids.user_id)

    mock_check_stream_access.assert_not_called()


@patch("app.services.permissions.check_stream_access")
@patch("app.services.permissions.task_crud.get_task_by_id")
def test_check_task_access_success(
    mock_get_task_by_id, mock_check_stream_access, mock_db, ids, mock_task
):
    stream_obj = Mock()
    project_obj = Mock()
    user_team = Mock(role_id=Role.EDITOR)
    mock_get_task_by_id.return_value = mock_task
    mock_check_stream_access.return_value = (stream_obj, project_obj, user_team)

    result_task, result_stream, result_project, result_user_team = check_task_access(
        mock_db, ids.task_id, ids.user_id, need_lead=True
    )

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id, need_lead=True
    )
    assert result_task is mock_task
    assert result_stream is stream_obj
    assert result_project is project_obj
    assert result_user_team is user_team


def test_check_editor_permission_forbidden():
    user_team = Mock(role_id=Role.READER)

    with pytest.raises(
        exception.ForbiddenError, match="У вас нет прав редактора для этого действия"
    ):
        check_editor_permission(user_team)


def test_check_editor_permission_success():
    user_team = Mock(role_id=Role.EDITOR)

    assert check_editor_permission(user_team) is None
