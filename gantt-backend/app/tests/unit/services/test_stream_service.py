from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.models.role import Role
from app.services.stream_service import (
    check_project_access,
    check_stream_access,
    check_admin_permission,
    get_project_streams_service,
    get_stream_service,
    create_stream_service,
    update_stream_service,
    delete_stream_service,
)


@patch("app.services.stream_service.team_crud.get_user_team_by_id")
@patch("app.services.stream_service.project_crud.get_project_by_id")
def test_check_project_access_success(mock_get_project, mock_get_user_team):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    project_obj = Mock(id=project_id, team_id=42)
    user_team = Mock()

    mock_get_project.return_value = project_obj
    mock_get_user_team.return_value = user_team

    result_project, result_user_team = check_project_access(
        mock_db, project_id, user_id
    )

    assert result_project is project_obj
    assert result_user_team is user_team


@patch("app.services.stream_service.project_crud.get_project_by_id")
def test_check_project_access_project_not_found(mock_get_project):
    mock_db = Mock()
    project_id = 42
    user_id = 42

    mock_get_project.return_value = None

    with pytest.raises(exception.NotFoundError):
        check_project_access(mock_db, project_id, user_id)


@patch("app.services.stream_service.team_crud.get_user_team_by_id")
@patch("app.services.stream_service.project_crud.get_project_by_id")
def test_check_project_access_user_not_in_team(mock_get_project, mock_get_user_team):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    project_obj = Mock(id=project_id, team_id=42)

    mock_get_project.return_value = project_obj
    mock_get_user_team.return_value = None

    with pytest.raises(exception.ForbiddenError):
        check_project_access(mock_db, project_id, user_id)


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.get_stream_by_id")
def test_check_stream_access_success(mock_get_stream, mock_check_project_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    stream_obj = Mock(id=stream_id, project_id=42)
    project_obj = Mock(id=42)
    user_team = Mock()

    mock_get_stream.return_value = stream_obj
    mock_check_project_access.return_value = (project_obj, user_team)

    result_stream, result_project, result_user_team = check_stream_access(
        mock_db, stream_id, user_id
    )

    assert result_stream is stream_obj
    assert result_project is project_obj
    assert result_user_team is user_team


@patch("app.services.stream_service.stream_crud.get_stream_by_id")
def test_check_stream_access_stream_not_found(mock_get_stream):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_get_stream.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        check_stream_access(mock_db, stream_id, user_id)


def test_check_admin_permission_success():
    user_team = Mock(role_id=Role.EDITOR)
    check_admin_permission(user_team)


def test_check_admin_permission_not_editor():
    user_team = Mock(role_id=Role.READER)
    with pytest.raises(exception.ForbiddenError):
        check_admin_permission(user_team)


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.get_streams_by_project_id")
def test_get_project_streams_service_success(mock_get_streams, mock_check_access):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    mock_streams = [Mock(), Mock()]

    mock_check_access.return_value = (Mock(), Mock())
    mock_get_streams.return_value = mock_streams

    result = get_project_streams_service(mock_db, project_id, user_id)

    mock_check_access.assert_called_once_with(mock_db, project_id, user_id)
    mock_get_streams.assert_called_once_with(mock_db, project_id)
    assert result == mock_streams


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.get_streams_by_project_id")
def test_get_project_streams_service_project_not_found(
    mock_get_streams, mock_check_access
):
    mock_db = Mock()
    project_id = 42
    user_id = 42

    mock_check_access.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_project_streams_service(mock_db, project_id, user_id)

    mock_get_streams.assert_not_called()


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.get_streams_by_project_id")
def test_get_project_streams_service_forbidden(mock_get_streams, mock_check_access):
    mock_db = Mock()
    project_id = 42
    user_id = 42

    mock_check_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_project_streams_service(mock_db, project_id, user_id)

    mock_get_streams.assert_not_called()


@patch("app.services.stream_service.check_stream_access")
def test_get_stream_service_success(mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    stream_obj = Mock(id=stream_id)

    mock_check_access.return_value = (stream_obj, Mock(), Mock())

    result = get_stream_service(mock_db, stream_id, user_id)

    mock_check_access.assert_called_once_with(mock_db, stream_id, user_id)
    assert result is stream_obj


@patch("app.services.stream_service.check_stream_access")
def test_get_stream_service_stream_not_found(mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_access.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_stream_service(mock_db, stream_id, user_id)


@patch("app.services.stream_service.check_stream_access")
def test_get_stream_service_forbidden(mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_stream_service(mock_db, stream_id, user_id)


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.get_stream_by_name_and_proj_id")
@patch("app.services.stream_service.stream_crud.create_new_stream")
def test_create_stream_service_success(
    mock_create, mock_get_by_name, mock_check_access
):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    stream_data = Mock()
    stream_data.name = "Test stream"
    user_team = Mock(role_id=Role.EDITOR)

    mock_check_access.return_value = (Mock(), user_team)
    mock_get_by_name.return_value = None
    expected_stream = Mock()
    mock_create.return_value = expected_stream

    result = create_stream_service(mock_db, project_id, stream_data, user_id)

    mock_check_access.assert_called_once_with(mock_db, project_id, user_id)
    mock_get_by_name.assert_called_once_with(mock_db, "Test stream", project_id)
    mock_create.assert_called_once_with(mock_db, project_id, stream_data)
    assert result is expected_stream


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.get_stream_by_name_and_proj_id")
@patch("app.services.stream_service.stream_crud.create_new_stream")
def test_create_stream_service_conflict(
    mock_create, mock_get_by_name, mock_check_access
):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    stream_data = Mock()
    stream_data.name = "Test stream duplicate"
    user_team = Mock(role_id=Role.EDITOR)

    mock_check_access.return_value = (Mock(), user_team)
    mock_get_by_name.return_value = Mock()

    with pytest.raises(exception.ConflictError):
        create_stream_service(mock_db, project_id, stream_data, user_id)

    mock_create.assert_not_called()


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.create_new_stream")
def test_create_stream_service_forbidden(mock_create, mock_check_access):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    stream_data = Mock()
    stream_data.name = "Test stream forbidden"
    user_team = Mock(role_id=Role.READER)

    mock_check_access.return_value = (Mock(), user_team)

    with pytest.raises(exception.ForbiddenError):
        create_stream_service(mock_db, project_id, stream_data, user_id)

    mock_create.assert_not_called()


@patch("app.services.stream_service.check_project_access")
@patch("app.services.stream_service.stream_crud.create_new_stream")
def test_create_stream_service_project_not_found(mock_create, mock_check_access):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    stream_data = Mock()
    stream_data.name = "Test stream"

    mock_check_access.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        create_stream_service(mock_db, project_id, stream_data, user_id)

    mock_create.assert_not_called()


@patch("app.services.stream_service.check_stream_access")
@patch("app.services.stream_service.stream_crud.update_stream")
def test_update_stream_service_success(mock_update, mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    stream_obj = Mock(id=stream_id)
    update_data = Mock()
    update_data.name = "Test stream updated"
    user_team = Mock(role_id=Role.EDITOR)

    mock_check_access.return_value = (stream_obj, Mock(), user_team)
    expected = Mock()
    mock_update.return_value = expected

    result = update_stream_service(mock_db, stream_id, update_data, user_id)

    mock_check_access.assert_called_once_with(mock_db, stream_id, user_id)
    mock_update.assert_called_once_with(mock_db, stream_obj, update_data)
    assert result is expected


@patch("app.services.stream_service.check_stream_access")
@patch("app.services.stream_service.stream_crud.update_stream")
def test_update_stream_service_forbidden(mock_update, mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    update_data = Mock()
    update_data.name = "Test stream updated"
    user_team = Mock(role_id=Role.READER)

    mock_check_access.return_value = (Mock(), Mock(), user_team)

    with pytest.raises(exception.ForbiddenError):
        update_stream_service(mock_db, stream_id, update_data, user_id)

    mock_update.assert_not_called()


@patch("app.services.stream_service.check_stream_access")
@patch("app.services.stream_service.stream_crud.update_stream")
def test_update_stream_service_stream_not_found(mock_update, mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    update_data = Mock()
    update_data.name = "Test stream updated"

    mock_check_access.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        update_stream_service(mock_db, stream_id, update_data, user_id)

    mock_update.assert_not_called()


@patch("app.services.stream_service.check_stream_access")
@patch("app.services.stream_service.stream_crud.delete_stream")
def test_delete_stream_service_success(mock_delete, mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    user_team = Mock(role_id=Role.EDITOR)

    mock_check_access.return_value = (Mock(), Mock(), user_team)

    delete_stream_service(mock_db, stream_id, user_id)

    mock_check_access.assert_called_once_with(mock_db, stream_id, user_id)
    mock_delete.assert_called_once_with(mock_db, stream_id)


@patch("app.services.stream_service.check_stream_access")
@patch("app.services.stream_service.stream_crud.delete_stream")
def test_delete_stream_service_forbidden(mock_delete, mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    user_team = Mock(role_id=Role.READER)

    mock_check_access.return_value = (Mock(), Mock(), user_team)

    with pytest.raises(exception.ForbiddenError):
        delete_stream_service(mock_db, stream_id, user_id)

    mock_delete.assert_not_called()


@patch("app.services.stream_service.check_stream_access")
@patch("app.services.stream_service.stream_crud.delete_stream")
def test_delete_stream_service_stream_not_found(mock_delete, mock_check_access):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_access.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        delete_stream_service(mock_db, stream_id, user_id)

    mock_delete.assert_not_called()
