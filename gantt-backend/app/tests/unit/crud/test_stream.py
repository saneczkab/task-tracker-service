import pytest

from app.core.exception import NotFoundError, ConflictError
from app.crud.stream import (
    get_streams_by_project_id,
    get_stream_by_id,
    get_stream_by_name_and_proj_id,
    create_new_stream,
    update_stream,
    delete_stream,
)
from app.schemas.stream import StreamCreate, StreamUpdate
from app.tests.factories import build_goal, build_task


def test_get_streams_by_project_id_returns_list(db_session, stream_obj):
    result = get_streams_by_project_id(db_session, stream_obj.project_id)
    assert len(result) == 1
    assert result[0].id == stream_obj.id


def test_get_streams_by_project_id_returns_empty_list(db_session):
    result = get_streams_by_project_id(db_session, 42)

    assert result == []


def test_get_stream_by_id_returns_stream(db_session, stream_obj):
    result = get_stream_by_id(db_session, stream_id=stream_obj.id)
    assert result.id == stream_obj.id


def test_get_stream_by_id_raises_not_found_when_missing(db_session):
    with pytest.raises(NotFoundError):
        get_stream_by_id(db_session, stream_id=42)


def test_get_stream_by_name_and_proj_id_found(db_session, stream_obj):
    result = get_stream_by_name_and_proj_id(
        db_session, name=stream_obj.name, proj_id=stream_obj.project_id
    )
    assert result.id == stream_obj.id


def test_get_stream_by_name_and_proj_id_not_found(db_session):
    result = get_stream_by_name_and_proj_id(db_session, name="Not exists", proj_id=42)

    assert result is None


def test_create_new_stream(db_session, project_obj):
    proj_id = project_obj.id
    stream_data = StreamCreate(name="Test stream")

    result = create_new_stream(db_session, proj_id, stream_data)

    assert result.name == stream_data.name
    assert result.project_id == proj_id
    assert result.id is not None


def test_create_new_stream_sets_correct_project_id(db_session, project_obj):
    proj_id = project_obj.id
    stream_data = StreamCreate(name="Test stream")

    result = create_new_stream(db_session, proj_id, stream_data)

    assert result.project_id == proj_id


def test_update_stream_updates_name(db_session, stream_obj):
    update_data = StreamUpdate(name="New name")

    result = update_stream(db_session, stream_obj, update_data)

    assert stream_obj.name == "New name"
    assert result is stream_obj


def test_update_stream_raises_conflict_when_name_already_exists(
    db_session, stream_obj, second_stream_obj
):
    second_stream_obj.name = "Occupied"
    db_session.commit()

    update_data = StreamUpdate(name="Occupied")

    with pytest.raises(ConflictError):
        update_stream(db_session, stream_obj, update_data)


def test_update_stream_same_name_no_db_check(db_session, stream_obj):
    update_data = StreamUpdate(name=stream_obj.name)
    result = update_stream(db_session, stream_obj, update_data)
    assert result is stream_obj


def test_update_stream_none_name_skips_update(db_session, stream_obj):
    previous_name = stream_obj.name
    update_data = StreamUpdate()

    result = update_stream(db_session, stream_obj, update_data)

    assert stream_obj.name == previous_name
    assert result is stream_obj


def test_delete_stream_deletes_tasks_goals_and_stream(db_session, stream_obj):
    task = build_task(task_id=50, stream_id=stream_obj.id, name="T")
    goal = build_goal(goal_id=50, stream_id=stream_obj.id, name="G")
    db_session.add(task)
    db_session.add(goal)
    db_session.commit()

    delete_stream(db_session, stream_obj.id)

    assert get_streams_by_project_id(db_session, stream_obj.project_id) == []


def test_delete_stream_raises_not_found_when_stream_missing(db_session):
    with pytest.raises(NotFoundError):
        delete_stream(db_session, stream_id=42)
