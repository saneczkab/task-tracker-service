from datetime import datetime
from unittest.mock import Mock

from app.crud.task import (
    get_task_by_id,
    get_tasks_by_stream,
    get_tasks_by_project,
    create_task,
    update_task,
    delete_task,
    create_task_relation,
)
from app.schemas.task import TaskCreate, TaskUpdate


def test_get_task_by_id_returns_task():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_task_by_id(mock_db, task_id=42)

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_task_by_id_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_task_by_id(mock_db, task_id=42)

    assert result is None


def test_get_tasks_by_stream_returns_list():
    mock_db = Mock()
    expected = [Mock(), Mock()]
    mock_db.query.return_value.filter.return_value.all.return_value = expected

    result = get_tasks_by_stream(mock_db, stream_id=42)

    assert result == expected
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_tasks_by_stream_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_tasks_by_stream(mock_db, stream_id=42)

    assert result == []


def test_get_tasks_by_project_returns_all_tasks():
    mock_db = Mock()

    stream1 = Mock()
    stream1.id = 42
    stream2 = Mock()
    stream2.id = 43

    project_obj = Mock()
    project_obj.streams = [stream1, stream2]

    tasks_stream1 = [Mock(), Mock()]
    tasks_stream2 = [Mock()]

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        tasks_stream1,
        tasks_stream2,
    ]

    result = get_tasks_by_project(mock_db, project_obj)

    assert result == tasks_stream1 + tasks_stream2


def test_get_tasks_by_project_returns_empty_list_when_no_streams():
    mock_db = Mock()
    project_obj = Mock()
    project_obj.streams = []

    result = get_tasks_by_project(mock_db, project_obj)

    assert result == []


def test_create_task():
    mock_db = Mock()
    stream_id = 42
    task_data = TaskCreate(
        name="Test task",
        description="Some description",
        status_id=1,
        priority_id=1,
        start_date=datetime(2025, 1, 1),
        deadline=datetime(2025, 6, 1),
        position=0,
    )

    result = create_task(mock_db, stream_id, task_data)

    assert result.name == task_data.name
    assert result.description == task_data.description
    assert result.stream_id == stream_id
    assert result.status_id == task_data.status_id
    assert result.priority_id == task_data.priority_id
    assert result.start_date == task_data.start_date
    assert result.deadline == task_data.deadline
    assert result.position == task_data.position

    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    assert result is added_obj


def test_create_task_uses_default_status_and_priority():
    mock_db = Mock()
    stream_id = 42
    task_data = TaskCreate(
        name="Test task",
        status_id=None,
        priority_id=None,
        position=0,
    )

    result = create_task(mock_db, stream_id, task_data)

    assert result.status_id == 1
    assert result.priority_id == 1


def test_create_task_uses_empty_string_when_no_description():
    mock_db = Mock()
    stream_id = 42
    task_data = TaskCreate(
        name="Test task",
        status_id=1,
        priority_id=1,
        position=0,
    )

    result = create_task(mock_db, stream_id, task_data)

    assert result.description == ""


def test_update_task_updates_fields():
    mock_db = Mock()
    task_obj = Mock()
    update_data = TaskUpdate(name="Updated task", description="New description")

    result = update_task(mock_db, task_obj, update_data)

    assert task_obj.name == "Updated task"
    assert task_obj.description == "New description"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(task_obj)
    assert result is task_obj


def test_update_task_only_provided_fields():
    mock_db = Mock()
    task_obj = Mock()
    update_data = TaskUpdate(name="Test")

    update_task(mock_db, task_obj, update_data)

    updated_fields = update_data.model_dump(exclude_unset=True)
    assert "name" in updated_fields
    assert "description" not in updated_fields
    assert "status_id" not in updated_fields


def test_update_task_empty_data():
    mock_db = Mock()
    task_obj = Mock()
    update_data = TaskUpdate()

    result = update_task(mock_db, task_obj, update_data)

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(task_obj)
    assert result is task_obj


def test_delete_task_calls_delete_and_commit():
    mock_db = Mock()
    task_obj = Mock()

    delete_task(mock_db, task_obj)

    mock_db.delete.assert_called_once_with(task_obj)
    mock_db.commit.assert_called_once()


def test_delete_task_does_not_refresh():
    mock_db = Mock()
    task_obj = Mock()

    delete_task(mock_db, task_obj)

    mock_db.refresh.assert_not_called()


def test_create_task_relation():
    mock_db = Mock()
    task_id_1 = 42
    task_id_2 = 43
    connection_id = 1

    result = create_task_relation(mock_db, task_id_1, task_id_2, connection_id)

    assert result.task_id_1 == task_id_1
    assert result.task_id_2 == task_id_2
    assert result.connection_id == connection_id

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)
    assert result is added_obj
