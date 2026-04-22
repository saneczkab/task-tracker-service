from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.services.stream_service import (
    create_stream_service,
    delete_stream_service,
    get_project_streams_service,
    get_stream_service,
    update_stream_service,
)


@patch("app.services.stream_service.stream_crud.get_streams_by_project_id")
@patch("app.services.stream_service.permissions.check_project_access")
def test_get_project_streams_service_success(
    mock_check_project_access, mock_get_streams, mock_db, ids
):
    expected_streams = [Mock(), Mock()]
    mock_get_streams.return_value = expected_streams

    result = get_project_streams_service(mock_db, ids.project_id, ids.user_id)

    mock_check_project_access.assert_called_once_with(
        mock_db, ids.project_id, ids.user_id
    )
    mock_get_streams.assert_called_once_with(mock_db, ids.project_id)
    assert result is expected_streams


@patch("app.services.stream_service.permissions.check_stream_access")
def test_get_stream_service_success(mock_check_stream_access, mock_db, ids):
    stream_obj = Mock(id=ids.stream_id)
    mock_check_stream_access.return_value = (stream_obj, Mock(), Mock())

    result = get_stream_service(mock_db, ids.stream_id, ids.user_id)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id
    )
    assert result is stream_obj


@patch.multiple(
    "app.services.stream_service.stream_crud",
    create_new_stream=DEFAULT,
    get_stream_by_name_and_proj_id=DEFAULT,
)
@patch.multiple(
    "app.services.stream_service.permissions",
    check_editor_permission=DEFAULT,
)
@patch("app.services.stream_service.permissions.check_project_access")
def test_create_stream_service_success_with_auto_position(
    mock_check_project_access,
    mock_db,
    ids,
    **mocks,
):
    stream_data = Mock(name="Sprint", position=None)
    user_team = Mock()
    last_stream = Mock(position=7)
    created_stream = Mock(id=ids.stream_id)

    mock_check_project_access.return_value = (Mock(id=ids.project_id), user_team)
    mocks["get_stream_by_name_and_proj_id"].return_value = None
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = last_stream
    mocks["create_new_stream"].return_value = created_stream

    result = create_stream_service(mock_db, ids.project_id, stream_data, ids.user_id)

    mock_check_project_access.assert_called_once_with(
        mock_db, ids.project_id, ids.user_id
    )
    mocks["check_editor_permission"].assert_called_once_with(user_team)
    mocks["get_stream_by_name_and_proj_id"].assert_called_once_with(
        mock_db,
        stream_data.name,
        ids.project_id,
    )
    assert stream_data.position == last_stream.position + 1
    mocks["create_new_stream"].assert_called_once_with(
        mock_db, ids.project_id, stream_data
    )
    assert result is created_stream


@patch.multiple(
    "app.services.stream_service.stream_crud",
    create_new_stream=DEFAULT,
    get_stream_by_name_and_proj_id=DEFAULT,
)
@patch.multiple(
    "app.services.stream_service.permissions",
    check_editor_permission=DEFAULT,
)
@patch("app.services.stream_service.permissions.check_project_access")
def test_create_stream_service_conflict(
    mock_check_project_access,
    mock_db,
    ids,
    **mocks,
):
    stream_data = Mock(name="Duplicate", position=1)
    mock_check_project_access.return_value = (Mock(), Mock())
    mocks["get_stream_by_name_and_proj_id"].return_value = Mock()

    with pytest.raises(exception.ConflictError):
        create_stream_service(mock_db, ids.project_id, stream_data, ids.user_id)

    mocks["create_new_stream"].assert_not_called()


@patch("app.services.stream_service.stream_crud.update_stream")
@patch.multiple(
    "app.services.stream_service.permissions",
    check_editor_permission=DEFAULT,
)
@patch("app.services.stream_service.permissions.check_stream_access")
def test_update_stream_service_success(
    mock_check_stream_access,
    mock_update_stream,
    mock_db,
    ids,
    **mocks,
):
    stream_obj = Mock(id=ids.stream_id)
    update_data = Mock(name="Updated")
    user_team = Mock()
    mock_check_stream_access.return_value = (stream_obj, Mock(), user_team)
    mock_update_stream.return_value = stream_obj

    result = update_stream_service(mock_db, ids.stream_id, update_data, ids.user_id)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id
    )
    mocks["check_editor_permission"].assert_called_once_with(user_team)
    mock_update_stream.assert_called_once_with(mock_db, stream_obj, update_data)
    assert result is stream_obj


@patch("app.services.stream_service.stream_crud.delete_stream")
@patch.multiple(
    "app.services.stream_service.permissions",
    check_editor_permission=DEFAULT,
)
@patch("app.services.stream_service.permissions.check_stream_access")
def test_delete_stream_service_success(
    mock_check_stream_access,
    mock_delete_stream,
    mock_db,
    ids,
    **mocks,
):
    user_team = Mock()
    mock_check_stream_access.return_value = (Mock(), Mock(), user_team)

    delete_stream_service(mock_db, ids.stream_id, ids.user_id)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id
    )
    mocks["check_editor_permission"].assert_called_once_with(user_team)
    mock_delete_stream.assert_called_once_with(mock_db, ids.stream_id)
