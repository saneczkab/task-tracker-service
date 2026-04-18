from datetime import datetime
from unittest.mock import Mock

from app.crud.goal import (
    create_goal,
    get_goal_by_id,
    get_goals_by_stream,
    get_goal_by_name_in_stream,
    update_goal,
    delete_goal,
)
from app.schemas.goal import GoalCreate, GoalUpdate


def test_create_goal():
    mock_db = Mock()
    stream_id = 42
    start_date = datetime(2025, 1, 1)
    deadline = datetime(2026, 2, 3)
    position = 24

    goal_data = GoalCreate(
        name="Test",
        description="Goal 123",
        start_date=start_date,
        deadline=deadline,
        position=position,
    )

    result = create_goal(mock_db, stream_id, goal_data)

    assert result.name == goal_data.name
    assert result.description == goal_data.description
    assert result.start_date == goal_data.start_date
    assert result.deadline == goal_data.deadline
    assert result.stream_id == stream_id
    assert result.position == goal_data.position

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)

    assert result is added_obj


def test_create_goal_minimum_data():
    mock_db = Mock()
    stream_id = 24
    deadline = datetime(2026, 2, 3)
    position = 42

    goal_data = GoalCreate(
        name="Test",
        deadline=deadline,
        position=position,
    )

    result = create_goal(mock_db, stream_id, goal_data)

    assert result.name == goal_data.name
    assert result.description == goal_data.description
    assert result.start_date == goal_data.start_date
    assert result.deadline == goal_data.deadline
    assert result.stream_id == stream_id
    assert result.position == goal_data.position

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)

    assert result is added_obj


def test_get_goal_by_id_returns_goal():
    mock_db = Mock()
    goal_id = 42
    expected_goal = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected_goal

    result = get_goal_by_id(mock_db, goal_id)

    assert result is expected_goal
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_goal_by_id_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_goal_by_id(mock_db, 999)

    assert result is None


def test_get_goals_by_stream_returns_list():
    mock_db = Mock()
    stream_id = 42
    expected_goals = [Mock(), Mock()]
    mock_db.query.return_value.filter.return_value.all.return_value = expected_goals

    result = get_goals_by_stream(mock_db, stream_id)

    assert result == expected_goals
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_goals_by_stream_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_goals_by_stream(mock_db, 99)

    assert result == []


def test_get_goal_by_name_in_stream_found():
    mock_db = Mock()
    stream_id = 42
    name = "Test goal"
    expected_goal = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected_goal

    result = get_goal_by_name_in_stream(mock_db, stream_id, name)

    assert result is expected_goal


def test_get_goal_by_name_in_stream_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_goal_by_name_in_stream(mock_db, 42, "Not exists")

    assert result is None


def test_get_goal_by_name_in_stream_with_exclude_id():
    mock_db = Mock()
    stream_id = 42
    name = "Test goal"
    exclude_id = 43
    expected_goal = Mock()
    mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = expected_goal

    result = get_goal_by_name_in_stream(mock_db, stream_id, name, exclude_id=exclude_id)

    assert result is expected_goal
    mock_db.query.return_value.filter.return_value.filter.return_value.first.assert_called_once()


def test_update_goal_updates_fields():
    mock_db = Mock()
    new_deadline = datetime(2026, 1, 2)

    goal_obj = Mock()
    goal_data = GoalUpdate(name="Updated", deadline=new_deadline)

    result = update_goal(mock_db, goal_obj, goal_data)

    assert goal_obj.name == "Updated"
    assert goal_obj.deadline == new_deadline
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(goal_obj)
    assert result is goal_obj


def test_update_goal_only_provided_fields():
    mock_db = Mock()

    goal_obj = Mock()
    goal_data = GoalUpdate(name="Test goal")

    update_goal(mock_db, goal_obj, goal_data)

    assert goal_obj.name == "Test goal"
    updated_fields = goal_data.model_dump(exclude_unset=True)
    assert "description" not in updated_fields
    assert "deadline" not in updated_fields


def test_update_goal_empty_data():
    mock_db = Mock()
    goal_obj = Mock()
    goal_data = GoalUpdate()

    result = update_goal(mock_db, goal_obj, goal_data)

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(goal_obj)
    assert result is goal_obj


def test_delete_goal_calls_delete_and_commit():
    mock_db = Mock()
    goal_obj = Mock()
    delete_goal(mock_db, goal_obj)

    mock_db.delete.assert_called_once_with(goal_obj)
    mock_db.commit.assert_called_once()


def test_delete_goal_does_not_refresh():
    mock_db = Mock()
    goal_obj = Mock()
    delete_goal(mock_db, goal_obj)

    mock_db.refresh.assert_not_called()
