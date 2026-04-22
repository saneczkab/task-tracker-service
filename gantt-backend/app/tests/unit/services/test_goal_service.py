from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.services.goal_service import (
    create_goal_service,
    delete_goal_service,
    get_stream_goals_service,
    update_goal_service,
)


@patch("app.services.goal_service.goal_crud.get_goals_by_stream")
@patch("app.services.goal_service.permissions.check_stream_access")
def test_get_stream_goals_service_success(
    mock_check_stream_access, mock_get_goals_by_stream, mock_db, ids
):
    expected_goals = [Mock(), Mock()]
    mock_get_goals_by_stream.return_value = expected_goals

    result = get_stream_goals_service(mock_db, ids.stream_id, ids.user_id)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id
    )
    mock_get_goals_by_stream.assert_called_once_with(mock_db, ids.stream_id)
    assert result is expected_goals


@patch.multiple(
    "app.services.goal_service.goal_crud",
    create_goal=DEFAULT,
    get_goal_by_name_in_stream=DEFAULT,
)
@patch("app.services.goal_service.permissions.check_stream_access")
def test_create_goal_service_sets_position_from_previous_goal(
    mock_check_stream_access,
    mock_db,
    ids,
    **mocks,
):
    goal_data = Mock(name="North Star", position=None)
    previous_goal = Mock(position=3)
    created_goal = Mock(id=ids.goal_id)

    mocks["get_goal_by_name_in_stream"].return_value = None
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = previous_goal
    mocks["create_goal"].return_value = created_goal

    result = create_goal_service(mock_db, ids.stream_id, ids.user_id, goal_data)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id, need_lead=True
    )
    mocks["get_goal_by_name_in_stream"].assert_called_once_with(
        mock_db,
        ids.stream_id,
        goal_data.name,
    )
    assert goal_data.position == previous_goal.position + 1
    mocks["create_goal"].assert_called_once_with(mock_db, ids.stream_id, goal_data)
    assert result is created_goal


@patch.multiple(
    "app.services.goal_service.goal_crud",
    create_goal=DEFAULT,
    get_goal_by_name_in_stream=DEFAULT,
)
@patch("app.services.goal_service.permissions.check_stream_access")
def test_create_goal_service_conflict(
    _mock_check_stream_access,
    mock_db,
    ids,
    **mocks,
):
    goal_data = Mock(name="Duplicate", position=1)
    mocks["get_goal_by_name_in_stream"].return_value = Mock()

    with pytest.raises(exception.ConflictError):
        create_goal_service(mock_db, ids.stream_id, ids.user_id, goal_data)

    mocks["create_goal"].assert_not_called()


@patch.multiple(
    "app.services.goal_service.goal_crud",
    update_goal=DEFAULT,
    get_goal_by_name_in_stream=DEFAULT,
)
@patch("app.services.goal_service.permissions.check_stream_access")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_update_goal_service_success(
    mock_get_goal_by_id,
    mock_check_stream_access,
    mock_db,
    ids,
    **mocks,
):
    goal_obj = Mock(id=ids.goal_id, stream_id=ids.stream_id, name="Old")
    goal_update_data = Mock(name="New")
    updated_goal = Mock(id=goal_obj.id)

    mock_get_goal_by_id.return_value = goal_obj
    mocks["get_goal_by_name_in_stream"].return_value = None
    mocks["update_goal"].return_value = updated_goal

    result = update_goal_service(mock_db, ids.goal_id, ids.user_id, goal_update_data)

    mock_get_goal_by_id.assert_called_once_with(mock_db, ids.goal_id)
    mock_check_stream_access.assert_called_once_with(
        mock_db, goal_obj.stream_id, ids.user_id, need_lead=True
    )
    mocks["get_goal_by_name_in_stream"].assert_called_once_with(
        mock_db,
        goal_obj.stream_id,
        goal_update_data.name,
        exclude_id=goal_obj.id,
    )
    mocks["update_goal"].assert_called_once_with(mock_db, goal_obj, goal_update_data)
    assert result is updated_goal


@patch.multiple("app.services.goal_service.goal_crud", delete_goal=DEFAULT)
@patch("app.services.goal_service.permissions.check_stream_access")
@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_delete_goal_service_success(
    mock_get_goal_by_id, mock_check_stream_access, mock_db, ids, **mocks
):
    goal_obj = Mock(id=ids.goal_id, stream_id=ids.stream_id)
    mock_get_goal_by_id.return_value = goal_obj

    delete_goal_service(mock_db, ids.goal_id, ids.user_id)

    mock_get_goal_by_id.assert_called_once_with(mock_db, ids.goal_id)
    mock_check_stream_access.assert_called_once_with(
        mock_db, goal_obj.stream_id, ids.user_id, need_lead=True
    )
    mocks["delete_goal"].assert_called_once_with(mock_db, goal_obj)


@patch("app.services.goal_service.goal_crud.get_goal_by_id")
def test_delete_goal_service_not_found(mock_get_goal_by_id, mock_db, ids):
    mock_get_goal_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_goal_service(mock_db, ids.goal_id, ids.user_id)
