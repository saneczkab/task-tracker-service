from datetime import datetime

from app.crud.task import (
    create_task_history_entries,
    get_task_by_id,
    get_task_history,
    get_tasks_by_project_ids,
    get_tasks_by_stream,
    get_tasks_by_stream_id,
    get_tasks_by_stream_ids,
    get_tasks_by_team_id,
    get_tasks_by_team_ids,
    get_tasks_by_user_id,
    get_tasks_by_project,
    create_task,
    update_task,
    delete_task,
    create_task_relation,
)
from app.models import meta as meta_model
from app.schemas.task import TaskCreate
from app.tests.factories import build_project, build_task, build_task_history


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
    db_session, project_obj, task_obj, second_task_obj, user_obj
):
    first = task_obj
    second = second_task_obj
    first.assigned_users.append(meta_model.UserTask(user_id=user_obj.id))
    db_session.commit()

    result = get_tasks_by_project(db_session, project_obj)
    assert len(result) == 2
    assert {item.id for item in result} == {first.id, second.id}

    result_by_id = {item.id: item for item in result}
    assert result_by_id[first.id].assignee_email == user_obj.email
    assert getattr(result_by_id[second.id], "assignee_email", None) is None


def test_get_tasks_by_project_returns_empty_list_when_no_streams(db_session, team_obj):
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
    update_fields = {"name": "Updated task", "description": "New description"}

    result = update_task(db_session, task_obj, update_fields)

    assert task_obj.name == "Updated task"
    assert task_obj.description == "New description"
    assert result is task_obj


def test_update_task_empty_data(db_session, task_obj):
    result = update_task(db_session, task_obj, {})

    assert result is task_obj


def test_delete_task_calls_delete_and_commit(db_session, task_obj):
    delete_task(db_session, task_obj)
    assert get_task_by_id(db_session, task_obj.id) is None


def test_create_task_relation(db_session, stream_obj, connection_type_obj):
    first_task = build_task(task_id=201, stream_id=stream_obj.id)
    second_task = build_task(task_id=202, stream_id=stream_obj.id)
    db_session.add(first_task)
    db_session.add(second_task)
    db_session.commit()

    result = create_task_relation(
        db_session, first_task.id, second_task.id, connection_type_obj.id
    )

    assert result.task_id_1 == first_task.id
    assert result.task_id_2 == second_task.id
    assert result.connection_id == connection_type_obj.id


def test_get_task_history_returns_entries_sorted_desc(db_session, task_obj, user_obj):
    older = build_task_history(
        history_id=301,
        task_id=task_obj.id,
        changed_by_id=user_obj.id,
        changed_at=datetime(2026, 1, 1, 10, 0, 0),
        field_name="name",
        old_value="A",
        new_value="B",
    )
    newer = build_task_history(
        history_id=302,
        task_id=task_obj.id,
        changed_by_id=user_obj.id,
        changed_at=datetime(2026, 1, 2, 10, 0, 0),
        field_name="status_id",
        old_value="1",
        new_value="2",
    )
    db_session.add(older)
    db_session.add(newer)
    db_session.commit()

    result = get_task_history(db_session, task_obj.id)

    assert len(result) == 2
    assert result[0].id == newer.id
    assert result[1].id == older.id


def test_get_tasks_by_user_id_returns_team_tasks(db_session, user_team_obj, task_obj):
    result = get_tasks_by_user_id(db_session, user_id=user_team_obj.user_id)

    assert len(result) == 1
    assert result[0].id == task_obj.id


def test_get_tasks_by_user_id_only_assigned_filters_result(
    db_session,
    user_team_obj,
    task_obj,
    second_task_obj,
):
    extra_task = second_task_obj

    assignment = meta_model.UserTask(user_id=user_team_obj.user_id, task_id=task_obj.id)
    db_session.add(assignment)
    db_session.commit()

    result = get_tasks_by_user_id(
        db_session,
        user_id=user_team_obj.user_id,
        only_assigned_to_user=True,
    )

    assert len(result) == 1
    assert result[0].id == task_obj.id
    assert result[0].id != extra_task.id


def test_get_tasks_by_team_id_filters_by_assigned_user(
    db_session,
    team_obj,
    user_obj,
    second_user_obj,
    task_obj,
    second_task_obj,
):
    first = task_obj
    second = second_task_obj

    db_session.add(meta_model.UserTask(user_id=user_obj.id, task_id=first.id))
    db_session.add(meta_model.UserTask(user_id=second_user_obj.id, task_id=second.id))
    db_session.commit()

    result = get_tasks_by_team_id(db_session, team_id=team_obj.id, user_id=user_obj.id)

    assert len(result) == 1
    assert result[0].id == first.id


def test_get_tasks_by_team_ids_filters_by_assigned_user(
    db_session,
    team_obj,
    second_user_obj,
    task_obj,
):
    target_task = task_obj

    db_session.add(
        meta_model.UserTask(user_id=second_user_obj.id, task_id=target_task.id)
    )
    db_session.commit()

    result = get_tasks_by_team_ids(
        db_session,
        team_ids=[team_obj.id],
        user_id=second_user_obj.id,
    )

    assert len(result) == 1
    assert result[0].id == target_task.id


def test_get_tasks_by_project_ids_filters_by_assigned_user(
    db_session,
    project_obj,
    user_obj,
    second_user_obj,
    task_obj,
    second_task_obj,
):
    first = task_obj
    second = second_task_obj

    db_session.add(meta_model.UserTask(user_id=user_obj.id, task_id=first.id))
    db_session.add(meta_model.UserTask(user_id=second_user_obj.id, task_id=second.id))
    db_session.commit()

    result = get_tasks_by_project_ids(
        db_session,
        project_ids=[project_obj.id],
        user_id=user_obj.id,
    )

    assert len(result) == 1
    assert result[0].id == first.id


def test_get_tasks_by_stream_id_filters_by_assigned_user(
    db_session,
    stream_obj,
    user_obj,
    second_user_obj,
):
    first = build_task(
        task_id=801,
        stream_id=stream_obj.id,
        name="S1",
    )
    second = build_task(
        task_id=802,
        stream_id=stream_obj.id,
        name="S2",
    )
    db_session.add(first)
    db_session.add(second)
    db_session.commit()

    db_session.add(meta_model.UserTask(user_id=user_obj.id, task_id=first.id))
    db_session.add(meta_model.UserTask(user_id=second_user_obj.id, task_id=second.id))
    db_session.commit()

    result = get_tasks_by_stream_id(
        db_session, stream_id=stream_obj.id, user_id=user_obj.id
    )

    assert len(result) == 1
    assert result[0].id == first.id
