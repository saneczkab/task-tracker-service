from unittest.mock import Mock

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


def test_get_streams_by_project_id_returns_list():
    mock_db = Mock()
    expected = [Mock(), Mock()]
    mock_db.query.return_value.filter.return_value.all.return_value = expected

    result = get_streams_by_project_id(mock_db, 42)

    assert result == expected
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_streams_by_project_id_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_streams_by_project_id(mock_db, 42)

    assert result == []


def test_get_stream_by_id_returns_stream():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_stream_by_id(mock_db, stream_id=42)

    assert result is expected


def test_get_stream_by_id_raises_not_found_when_missing():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError):
        get_stream_by_id(mock_db, stream_id=42)


def test_get_stream_by_name_and_proj_id_found():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_stream_by_name_and_proj_id(mock_db, name="Test", proj_id=42)

    assert result is expected


def test_get_stream_by_name_and_proj_id_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_stream_by_name_and_proj_id(mock_db, name="Not exists", proj_id=42)

    assert result is None


def test_create_new_stream():
    mock_db = Mock()
    proj_id = 42
    stream_data = StreamCreate(name="Test stream")

    result = create_new_stream(mock_db, proj_id, stream_data)

    assert result.name == stream_data.name
    assert result.project_id == proj_id

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


def test_create_new_stream_sets_correct_project_id():
    mock_db = Mock()
    proj_id = 42
    stream_data = StreamCreate(name="Test stream")

    result = create_new_stream(mock_db, proj_id, stream_data)

    assert result.project_id == proj_id


def test_update_stream_updates_name():
    mock_db = Mock()
    stream_obj = Mock()
    stream_obj.name = "Test"
    stream_obj.id = 42
    stream_obj.project_id = 42

    mock_db.query.return_value.filter.return_value.first.return_value = None
    update_data = StreamUpdate(name="New name")

    result = update_stream(mock_db, stream_obj, update_data)

    assert stream_obj.name == "New name"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(stream_obj)
    assert result is stream_obj


def test_update_stream_raises_conflict_when_name_already_exists():
    mock_db = Mock()
    stream_obj = Mock()
    stream_obj.name = "Stream test"
    stream_obj.id = 42
    stream_obj.project_id = 42

    mock_db.query.return_value.filter.return_value.first.return_value = Mock()
    update_data = StreamUpdate(name="Stream test 2")

    with pytest.raises(ConflictError):
        update_stream(mock_db, stream_obj, update_data)

    mock_db.commit.assert_not_called()


def test_update_stream_same_name_no_db_check():
    mock_db = Mock()
    stream_obj = Mock()
    stream_obj.name = "Stream test"
    stream_obj.id = 42
    stream_obj.project_id = 42

    update_data = StreamUpdate(name="Stream test")

    result = update_stream(mock_db, stream_obj, update_data)

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(stream_obj)
    assert result is stream_obj


def test_update_stream_none_name_skips_update():
    mock_db = Mock()
    stream_obj = Mock()
    stream_obj.name = "Stream test"
    update_data = StreamUpdate()

    result = update_stream(mock_db, stream_obj, update_data)

    assert stream_obj.name == "Stream test"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(stream_obj)
    assert result is stream_obj


def test_delete_stream_deletes_tasks_goals_and_stream():
    mock_db = Mock()
    stream_id = 42
    stream_obj = Mock()

    mock_db.query.return_value.filter.return_value.first.return_value = stream_obj

    delete_stream(mock_db, stream_id)

    mock_db.delete.assert_called_once_with(stream_obj)
    mock_db.commit.assert_called_once()

    assert mock_db.query.return_value.filter.return_value.delete.call_count == 2


def test_delete_stream_raises_not_found_when_stream_missing():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError):
        delete_stream(mock_db, stream_id=42)

    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()
