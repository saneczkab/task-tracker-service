from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.goal import GoalCreate, GoalUpdate


def test_goal_create_min_payload():
    deadline = GoalCreate(name="Goal")
    assert deadline.name == "Goal"
    assert deadline.description is None
    assert deadline.start_date is None
    assert deadline.deadline is None


def test_goal_create_empty_name():
    with pytest.raises(ValidationError):
        GoalCreate(name="")


@pytest.mark.parametrize("pos", [-1, -10])
def test_goal_create_negative_position(pos: int):
    with pytest.raises(ValidationError):
        GoalCreate(name="Goal", position=pos)


def test_goal_create_deadline_after_start_date():
    start = datetime.now() + timedelta(days=1)
    deadline = start + timedelta(hours=1)
    result = GoalCreate(name="Goal", start_date=start, deadline=deadline)
    assert result.deadline == deadline


def test_goal_create_deadline_equal_to_start_date():
    start = datetime.now() + timedelta(days=1)
    with pytest.raises(ValidationError):
        GoalCreate(name="Goal", start_date=start, deadline=start)


def test_goal_create_deadline_before_start_date():
    start = datetime.now() + timedelta(days=2)
    deadline = start - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        GoalCreate(name="Goal", start_date=start, deadline=deadline)


def test_goal_update_empty_name():
    with pytest.raises(ValidationError):
        GoalUpdate(name="")


@pytest.mark.parametrize("pos", [-1, -10])
def test_goal_update_negative_position(pos: int):
    with pytest.raises(ValidationError):
        GoalUpdate(position=pos)


def test_goal_update_deadline_after_start_date():
    start = datetime.now() + timedelta(days=1)
    deadline = start + timedelta(hours=1)
    result = GoalUpdate(start_date=start, deadline=deadline)
    assert result.deadline == deadline


def test_goal_update_deadline_equal_to_start_date():
    start = datetime.now() + timedelta(days=1)
    with pytest.raises(ValidationError):
        GoalUpdate(start_date=start, deadline=start)


def test_goal_update_deadline_before_start_date():
    start = datetime.now() + timedelta(days=2)
    deadline = start - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        GoalUpdate(start_date=start, deadline=deadline)
