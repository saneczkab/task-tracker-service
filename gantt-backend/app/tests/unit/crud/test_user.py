import pytest

from app.core.exception import ConflictError, NotFoundError
from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_nickname,
)


def test_get_user_by_id_returns_user(db_session, user_obj):
    result = get_user_by_id(db_session, user_id=user_obj.id)
    assert result.id == user_obj.id


def test_get_user_by_id_raises_not_found_when_missing(db_session):
    with pytest.raises(NotFoundError):
        get_user_by_id(db_session, user_id=999)


def test_get_user_by_email_returns_user(db_session, user_obj):
    result = get_user_by_email(db_session, email=user_obj.email)
    assert result.id == user_obj.id


def test_get_user_by_email_returns_none_when_not_found(db_session):
    result = get_user_by_email(db_session, email="not-exist@test.com")
    assert result is None


def test_get_user_by_nickname_returns_user(db_session, user_obj):
    result = get_user_by_nickname(db_session, nickname=user_obj.nickname)
    assert result.id == user_obj.id


def test_get_user_by_nickname_returns_none_when_not_found(db_session):
    result = get_user_by_nickname(db_session, nickname="not_exist")
    assert result is None


def test_create_user(db_session):
    result = create_user(
        db_session,
        email="new@test.com",
        nickname="new_user",
        password_hash="hash",
    )

    assert result.email == "new@test.com"
    assert result.nickname == "new_user"
    assert result.password_hash == "hash"
    assert result.id is not None


def test_create_user_raises_conflict_on_integrity_error(db_session, user_obj):
    with pytest.raises(ConflictError):
        create_user(
            db_session,
            email=user_obj.email,
            nickname="another_nick",
            password_hash="hash",
        )


def test_create_user_rollback_keeps_session_usable(db_session, user_obj):
    with pytest.raises(ConflictError):
        create_user(
            db_session,
            email=user_obj.email,
            nickname="another_nick",
            password_hash="hash",
        )

    created = create_user(
        db_session,
        email="ok@test.com",
        nickname="ok_nick",
        password_hash="hash",
    )
    assert created.email == "ok@test.com"
