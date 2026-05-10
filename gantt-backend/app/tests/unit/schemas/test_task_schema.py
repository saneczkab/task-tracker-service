from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.task import TaskCreate, TaskUpdate


def test_task_create_min_payload():
    result = TaskCreate(name="Task")
    assert result.name == "Task"
    assert result.description is None
    assert result.status_id is None
    assert result.priority_id is None
    assert result.assignee_email is None
    assert result.start_date is None
    assert result.deadline is None


def test_task_create_empty_name():
    with pytest.raises(ValidationError):
        TaskCreate(name="")


@pytest.mark.parametrize("value", [0, -1])
def test_task_create_non_positive_status_id(value: int):
    with pytest.raises(ValidationError):
        TaskCreate(name="Task", status_id=value)


@pytest.mark.parametrize("value", [0, -1])
def test_task_create_non_positive_priority_id(value: int):
    with pytest.raises(ValidationError):
        TaskCreate(name="Task", priority_id=value)


@pytest.mark.parametrize("value", [-1, -10])
def test_task_create_negative_position(value: int):
    with pytest.raises(ValidationError):
        TaskCreate(name="Task", position=value)


def test_task_create_deadline_after_start_date():
    start = datetime.now() + timedelta(days=1)
    deadline = start + timedelta(hours=1)
    result = TaskCreate(name="Task", start_date=start, deadline=deadline)
    assert result.deadline == deadline


def test_task_create_deadline_equal_to_start_date():
    start = datetime.now() + timedelta(days=1)
    with pytest.raises(ValidationError):
        TaskCreate(name="Task", start_date=start, deadline=start)


def test_task_create_deadline_before_start_date():
    start = datetime.now() + timedelta(days=2)
    deadline = start - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        TaskCreate(name="Task", start_date=start, deadline=deadline)


def test_task_update_empty_payload():
    result = TaskUpdate()
    assert result.name is None


def test_task_update_empty_name():
    with pytest.raises(ValidationError):
        TaskUpdate(name="")


@pytest.mark.parametrize("value", [0, -1])
def test_task_update_non_positive_status_id(value: int):
    with pytest.raises(ValidationError):
        TaskUpdate(status_id=value)


@pytest.mark.parametrize("value", [0, -1])
def test_task_update_non_positive_priority_id(value: int):
    with pytest.raises(ValidationError):
        TaskUpdate(priority_id=value)


@pytest.mark.parametrize("value", [-1, -10])
def test_task_update_negative_position(value: int):
    with pytest.raises(ValidationError):
        TaskUpdate(position=value)


def test_task_update_deadline_after_start_date():
    start = datetime.now() + timedelta(days=1)
    deadline = start + timedelta(hours=1)
    result = TaskUpdate(start_date=start, deadline=deadline)
    assert result.deadline == deadline


def test_task_update_deadline_equal_to_start_date():
    start = datetime.now() + timedelta(days=1)
    with pytest.raises(ValidationError):
        TaskUpdate(start_date=start, deadline=start)


def test_task_update_deadline_before_start_date():
    start = datetime.now() + timedelta(days=2)
    deadline = start - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        TaskUpdate(start_date=start, deadline=deadline)
