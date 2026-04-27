from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.services.goal_service import (
    get_stream_goals_service,
    create_goal_service,
    update_goal_service,
    delete_goal_service,
)


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goals_by_stream")
def test_get_stream_goals_service_success(mock_get_goals, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    mock_goals = [Mock(), Mock()]

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_get_goals.return_value = mock_goals

    result = get_stream_goals_service(mock_db, stream_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, stream_id, user_id)
    mock_get_goals.assert_called_once_with(mock_db, stream_id)
    assert result == mock_goals


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goals_by_stream")
def test_get_stream_goals_service_forbidden(mock_get_goals, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_stream_goals_service(mock_db, stream_id, user_id)

    mock_get_goals.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goals_by_stream")
def test_get_stream_goals_service_stream_not_found(mock_get_goals, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_stream_goals_service(mock_db, stream_id, user_id)

    mock_get_goals.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
@patch("app.services.goal_service.goal_crud.create_goal")
def test_create_goal_service_success_with_position(
    mock_create, mock_get_by_name, mock_check_perms
):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    goal_data = Mock()
    goal_data.name = "Test goal"
    goal_data.position = 1

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_get_by_name.return_value = None
    expected_goal = Mock()
    mock_create.return_value = expected_goal

    result = create_goal_service(mock_db, stream_id, user_id, goal_data)

    mock_check_perms.assert_called_once_with(
        mock_db, stream_id, user_id, need_lead=True
    )
    mock_get_by_name.assert_called_once_with(mock_db, stream_id, "Test goal")
    mock_create.assert_called_once_with(mock_db, stream_id, goal_data)
    assert result is expected_goal


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
@patch("app.services.goal_service.goal_crud.create_goal")
def test_create_goal_service_auto_position_no_previous(
    mock_create, mock_get_by_name, mock_check_perms
):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    goal_data = Mock()
    goal_data.name = "Test goal"
    goal_data.position = None

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_get_by_name.return_value = None
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
    mock_create.return_value = Mock()

    create_goal_service(mock_db, stream_id, user_id, goal_data)

    assert goal_data.position == 1


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
@patch("app.services.goal_service.goal_crud.create_goal")
def test_create_goal_service_auto_position_with_previous(
    mock_create, mock_get_by_name, mock_check_perms
):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    goal_data = Mock()
    goal_data.name = "Test goal"
    goal_data.position = None
    last_goal = Mock(position=3)

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_get_by_name.return_value = None
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = last_goal
    mock_create.return_value = Mock()

    create_goal_service(mock_db, stream_id, user_id, goal_data)

    assert goal_data.position == 4


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
@patch("app.services.goal_service.goal_crud.create_goal")
def test_create_goal_service_conflict_on_duplicate_name(
    mock_create, mock_get_by_name, mock_check_perms
):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    goal_data = Mock()
    goal_data.name = "Test goal"
    goal_data.position = 1

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_get_by_name.return_value = Mock()

    with pytest.raises(exception.ConflictError):
        create_goal_service(mock_db, stream_id, user_id, goal_data)

    mock_create.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
def test_create_goal_service_forbidden(mock_get_by_name, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    goal_data = Mock()
    goal_data.name = "Test goal"
    goal_data.position = 1

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        create_goal_service(mock_db, stream_id, user_id, goal_data)

    mock_get_by_name.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
@patch("app.services.goal_service.goal_crud.update_goal")
def test_update_goal_service_success(
    mock_update, mock_get_by_name, mock_get_by_id, mock_check_perms
):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)
    goal_obj.name = "Test goal"
    goal_update_data = Mock()
    goal_update_data.name = "Test goal 2"

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.return_value = Mock(id=42)
    mock_get_by_name.return_value = None
    expected = Mock()
    mock_update.return_value = expected

    result = update_goal_service(mock_db, goal_id, user_id, goal_update_data)

    mock_get_by_id.assert_called_once_with(mock_db, goal_id)
    mock_check_perms.assert_called_once_with(
        mock_db, goal_obj.stream_id, user_id, need_lead=True
    )
    mock_get_by_name.assert_called_once_with(
        mock_db, goal_obj.stream_id, "Test goal 2", exclude_id=goal_id
    )
    mock_update.assert_called_once_with(mock_db, goal_obj, goal_update_data)
    assert result is expected


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
@patch("app.services.goal_service.goal_crud.update_goal")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
def test_update_goal_service_same_name_skips_duplicate_check(
    mock_get_by_name, mock_update, mock_get_by_id, mock_check_perms
):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)
    goal_obj.name = "Test goal"
    goal_update_data = Mock()
    goal_update_data.name = "Test goal"

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.return_value = Mock(id=42)
    mock_update.return_value = Mock()

    update_goal_service(mock_db, goal_id, user_id, goal_update_data)
    mock_get_by_name.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
@patch("app.services.goal_service.goal_crud.update_goal")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
def test_update_goal_service_no_name_skips_duplicate_check(
    mock_get_by_name, mock_update, mock_get_by_id, mock_check_perms
):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)
    goal_obj.name = "Test goal"
    goal_update_data = Mock()
    goal_update_data.name = None

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.return_value = Mock(id=42)
    mock_update.return_value = Mock()

    update_goal_service(mock_db, goal_id, user_id, goal_update_data)
    mock_get_by_name.assert_not_called()


@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_update_goal_service_goal_not_found(mock_get_by_id):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_update_data = Mock()
    goal_update_data.name = "Test goal"

    mock_get_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_goal_service(mock_db, goal_id, user_id, goal_update_data)


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
@patch("app.services.goal_service.goal_crud.get_goal_by_name_in_stream")
@patch("app.services.goal_service.goal_crud.update_goal")
def test_update_goal_service_conflict_on_duplicate_name(
    mock_update, mock_get_by_name, mock_get_by_id, mock_check_perms
):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)
    goal_obj.name = "Test goal"
    goal_update_data = Mock()
    goal_update_data.name = "Test goal 2"

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.return_value = Mock(id=42)
    mock_get_by_name.return_value = Mock()

    with pytest.raises(exception.ConflictError):
        update_goal_service(mock_db, goal_id, user_id, goal_update_data)

    mock_update.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_update_goal_service_forbidden(mock_get_by_id, mock_check_perms):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)
    goal_obj.name = "Test goal"
    goal_update_data = Mock()
    goal_update_data.name = "Test goal 2"

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        update_goal_service(mock_db, goal_id, user_id, goal_update_data)


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
@patch("app.services.goal_service.goal_crud.delete_goal")
def test_delete_goal_service_success(mock_delete, mock_get_by_id, mock_check_perms):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.return_value = Mock(id=42)

    delete_goal_service(mock_db, goal_id, user_id)

    mock_get_by_id.assert_called_once_with(mock_db, goal_id)
    mock_check_perms.assert_called_once_with(
        mock_db, goal_obj.stream_id, user_id, need_lead=True
    )
    mock_delete.assert_called_once_with(mock_db, goal_obj)


@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_delete_goal_service_goal_not_found(mock_get_by_id):
    mock_db = Mock()
    goal_id = 42
    user_id = 42

    mock_get_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_goal_service(mock_db, goal_id, user_id)


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
@patch("app.services.goal_service.goal_crud.delete_goal")
def test_delete_goal_service_forbidden(mock_delete, mock_get_by_id, mock_check_perms):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_goal_service(mock_db, goal_id, user_id)

    mock_delete.assert_not_called()


@patch("app.services.goal_service.check_stream_permissions")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_delete_goal_service_stream_not_found(mock_get_by_id, mock_check_perms):
    mock_db = Mock()
    goal_id = 42
    user_id = 42
    goal_obj = Mock(id=goal_id, stream_id=42)

    mock_get_by_id.return_value = goal_obj
    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        delete_goal_service(mock_db, goal_id, user_id)
