import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError

from app.crud.user import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_nickname,
    create_user,
)
from app.core.exception import NotFoundError, ConflictError


def test_get_user_by_id_returns_user():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_user_by_id(mock_db, user_id=42)

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_user_by_id_raises_not_found_when_missing():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError):
        get_user_by_id(mock_db, user_id=42)


def test_get_user_by_email_returns_user():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_user_by_email(mock_db, email="test@test.com")

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_user_by_email_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_user_by_email(mock_db, email="not-exist@test.com")

    assert result is None


def test_get_user_by_nickname_returns_user():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_user_by_nickname(mock_db, nickname="test_nick")

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_user_by_nickname_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_user_by_nickname(mock_db, nickname="not_exist")

    assert result is None


def test_create_user():
    mock_db = Mock()

    result = create_user(
        mock_db,
        email="test@test.com",
        nickname="test",
        password_hash="hash",
    )

    assert result.email == "test@test.com"
    assert result.nickname == "test"
    assert result.password_hash == "hash"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


def test_create_user_raises_conflict_on_integrity_error():
    mock_db = Mock()
    mock_db.commit.side_effect = IntegrityError(None, None, None)

    with pytest.raises(ConflictError):
        create_user(
            mock_db,
            email="test@test.com",
            nickname="test",
            password_hash="hash",
        )

    mock_db.rollback.assert_called_once()


def test_create_user_does_not_refresh_on_integrity_error():
    mock_db = Mock()
    mock_db.commit.side_effect = IntegrityError(None, None, None)

    with pytest.raises(ConflictError):
        create_user(
            mock_db,
            email="test@test.com",
            nickname="test",
            password_hash="hash",
        )

    mock_db.refresh.assert_not_called()
