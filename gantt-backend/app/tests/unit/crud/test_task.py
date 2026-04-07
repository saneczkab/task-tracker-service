from datetime import datetime

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
from app.tests.factories import build_task


def test_get_task_by_id_returns_task(db_session, task_obj):
    result = get_task_by_id(db_session, task_id=task_obj.id)
    assert result.id == task_obj.id


def test_get_task_by_id_returns_none_when_not_found(db_session):
    result = get_task_by_id(db_session, task_id=42)

    assert result is None


def test_get_tasks_by_stream_returns_list(db_session, task_obj):
    result = get_tasks_by_stream(db_session, stream_id=task_obj.stream_id)
    assert len(result) == 1
    assert result[0].id == task_obj.id


def test_get_tasks_by_stream_returns_empty_list(db_session):
    result = get_tasks_by_stream(db_session, stream_id=42)

    assert result == []


def test_get_tasks_by_project_returns_all_tasks(
    db_session, project_obj, stream_obj, second_stream_obj
):
    first = build_task(task_id=101, stream_id=stream_obj.id, name="First")
    second = build_task(task_id=102, stream_id=second_stream_obj.id, name="Second")
    db_session.add(first)
    db_session.add(second)
    db_session.commit()

    result = get_tasks_by_project(db_session, project_obj)
    assert len(result) == 2
    assert {item.id for item in result} == {101, 102}


def test_get_tasks_by_project_returns_empty_list_when_no_streams(db_session, team_obj):
    from app.tests.factories import build_project

    empty_project = build_project(project_id=900, name="Empty", team_id=team_obj.id)
    db_session.add(empty_project)
    db_session.commit()

    result = get_tasks_by_project(db_session, empty_project)

    assert result == []


def test_create_task(db_session, stream_obj):
    stream_id = stream_obj.id
    task_data = TaskCreate(
        name="Test task",
        description="Some description",
        status_id=1,
        priority_id=1,
        start_date=datetime(2025, 1, 1),
        deadline=datetime(2025, 6, 1),
        position=0,
    )

    result = create_task(db_session, stream_id, task_data)

    assert result.name == task_data.name
    assert result.description == task_data.description
    assert result.stream_id == stream_id
    assert result.status_id == task_data.status_id
    assert result.priority_id == task_data.priority_id
    assert result.start_date == task_data.start_date
    assert result.deadline == task_data.deadline
    assert result.position == task_data.position
    assert result.id is not None


def test_create_task_uses_default_status_and_priority(db_session, stream_obj):
    stream_id = stream_obj.id
    task_data = TaskCreate(
        name="Test task",
        status_id=None,
        priority_id=None,
        position=0,
    )

    result = create_task(db_session, stream_id, task_data)

    assert result.status_id == 1
    assert result.priority_id == 1


def test_create_task_uses_empty_string_when_no_description(db_session, stream_obj):
    stream_id = stream_obj.id
    task_data = TaskCreate(
        name="Test task",
        status_id=1,
        priority_id=1,
        position=0,
    )

    result = create_task(db_session, stream_id, task_data)

    assert result.description == ""


def test_update_task_updates_fields(db_session, task_obj):
    update_data = TaskUpdate(name="Updated task", description="New description")

    result = update_task(db_session, task_obj, update_data)

    assert task_obj.name == "Updated task"
    assert task_obj.description == "New description"
    assert result is task_obj


def test_update_task_only_provided_fields(db_session, task_obj):
    update_data = TaskUpdate(name="Test")

    update_task(db_session, task_obj, update_data)

    updated_fields = update_data.model_dump(exclude_unset=True)
    assert "name" in updated_fields
    assert "description" not in updated_fields
    assert "status_id" not in updated_fields


def test_update_task_empty_data(db_session, task_obj):
    update_data = TaskUpdate()

    result = update_task(db_session, task_obj, update_data)

    assert result is task_obj


def test_delete_task_calls_delete_and_commit(db_session, task_obj):
    delete_task(db_session, task_obj)
    assert get_task_by_id(db_session, task_obj.id) is None


def test_delete_task_does_not_refresh(db_session, task_obj):
    delete_task(db_session, task_obj)
    assert get_tasks_by_stream(db_session, task_obj.stream_id) == []


def test_create_task_relation(db_session, stream_obj, connection_type_obj):
    first_task = build_task(task_id=42, stream_id=stream_obj.id, name="A")
    second_task = build_task(task_id=43, stream_id=stream_obj.id, name="B")
    db_session.add(first_task)
    db_session.add(second_task)
    db_session.commit()

    result = create_task_relation(db_session, 42, 43, connection_type_obj.id)

    assert result.task_id_1 == 42
    assert result.task_id_2 == 43
    assert result.connection_id == connection_type_obj.id
