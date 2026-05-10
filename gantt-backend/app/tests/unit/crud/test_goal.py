from datetime import datetime

from app.crud.goal import (
    create_goal,
    get_goal_by_id,
    get_goals_by_stream,
    get_goal_by_name_in_stream,
    update_goal,
    delete_goal,
)
from app.schemas.goal import GoalCreate, GoalUpdate


def test_create_goal(db_session, stream_obj):
    stream_id = stream_obj.id
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

    result = create_goal(db_session, stream_id, goal_data)

    assert result.name == goal_data.name
    assert result.description == goal_data.description
    assert result.start_date == goal_data.start_date
    assert result.deadline == goal_data.deadline
    assert result.stream_id == stream_id
    assert result.position == goal_data.position

    assert result.id is not None


def test_create_goal_minimum_data(db_session, stream_obj):
    stream_id = stream_obj.id
    deadline = datetime(2026, 2, 3)
    position = 42

    goal_data = GoalCreate(
        name="Test",
        deadline=deadline,
        position=position,
    )

    result = create_goal(db_session, stream_id, goal_data)

    assert result.name == goal_data.name
    assert result.description == goal_data.description
    assert result.start_date == goal_data.start_date
    assert result.deadline == goal_data.deadline
    assert result.stream_id == stream_id
    assert result.position == goal_data.position

    assert result.id is not None


def test_get_goal_by_id_returns_goal(db_session, goal_obj):
    result = get_goal_by_id(db_session, goal_obj.id)
    assert result.id == goal_obj.id


def test_get_goal_by_id_returns_none_when_not_found(db_session):
    result = get_goal_by_id(db_session, 999)

    assert result is None


def test_get_goals_by_stream_returns_list(db_session, goal_obj):
    result = get_goals_by_stream(db_session, goal_obj.stream_id)
    assert len(result) == 1
    assert result[0].id == goal_obj.id


def test_get_goals_by_stream_returns_empty_list(db_session):
    result = get_goals_by_stream(db_session, 99)

    assert result == []


def test_get_goal_by_name_in_stream_found(db_session, goal_obj):
    result = get_goal_by_name_in_stream(db_session, goal_obj.stream_id, goal_obj.name)
    assert result.id == goal_obj.id


def test_get_goal_by_name_in_stream_not_found(db_session, stream_obj):
    result = get_goal_by_name_in_stream(db_session, stream_obj.id, "Not exists")

    assert result is None


def test_get_goal_by_name_in_stream_with_exclude_id(db_session, stream_obj, goal_obj):
    stream_id = stream_obj.id
    name = "Test goal"
    other_goal = create_goal(
        db_session,
        stream_id,
        GoalCreate(name=name, deadline=datetime(2026, 3, 3), position=2),
    )

    result = get_goal_by_name_in_stream(
        db_session, stream_id, name, exclude_id=goal_obj.id
    )
    assert result.id == other_goal.id


def test_update_goal_updates_fields(db_session, goal_obj):
    new_deadline = datetime(2026, 1, 2)
    goal_data = GoalUpdate(name="Updated", deadline=new_deadline)

    result = update_goal(db_session, goal_obj, goal_data)

    assert goal_obj.name == "Updated"
    assert goal_obj.deadline == new_deadline
    assert result is goal_obj


def test_update_goal_only_provided_fields(db_session, goal_obj):
    goal_data = GoalUpdate(name="Test goal")

    update_goal(db_session, goal_obj, goal_data)

    assert goal_obj.name == "Test goal"
    updated_fields = goal_data.model_dump(exclude_unset=True)
    assert "description" not in updated_fields
    assert "deadline" not in updated_fields


def test_update_goal_empty_data(db_session, goal_obj):
    goal_data = GoalUpdate()

    result = update_goal(db_session, goal_obj, goal_data)

    assert result is goal_obj


def test_delete_goal_calls_delete_and_commit(db_session, goal_obj):
    delete_goal(db_session, goal_obj)
    assert get_goal_by_id(db_session, goal_obj.id) is None


def test_delete_goal_does_not_refresh(db_session, goal_obj):
    delete_goal(db_session, goal_obj)
    assert get_goals_by_stream(db_session, goal_obj.stream_id) == []
