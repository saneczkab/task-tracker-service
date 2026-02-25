from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.services.user_service import (
    get_current_user_service,
    check_email_exists_service,
    register_user_service,
    login_user_service,
    get_user_by_token_service,
    get_user_service,
)


@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_current_user_service_success(mock_get_user):
    mock_db = Mock()
    user_id = 42
    user_obj = Mock(id=user_id)

    mock_get_user.return_value = user_obj

    result = get_current_user_service(mock_db, user_id)

    mock_get_user.assert_called_once_with(mock_db, user_id)
    assert result is user_obj


@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_current_user_service_not_found(mock_get_user):
    mock_db = Mock()
    user_id = 42

    mock_get_user.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_current_user_service(mock_db, user_id)


@patch("app.services.user_service.user_crud.get_user_by_email")
def test_check_email_exists_service_exists(mock_get_by_email):
    mock_db = Mock()

    mock_get_by_email.return_value = Mock(id=42, email="test@test.com")

    result = check_email_exists_service(mock_db, "test@test.com")

    mock_get_by_email.assert_called_once_with(mock_db, "test@test.com")
    assert result is True


@patch("app.services.user_service.user_crud.get_user_by_email")
def test_check_email_exists_service_not_exists(mock_get_by_email):
    mock_db = Mock()
    mock_get_by_email.return_value = None

    result = check_email_exists_service(mock_db, "test@test.com")

    assert result is False


@patch("app.services.user_service.security.create_access_token")
@patch("app.services.user_service.security.get_password_hash")
@patch("app.services.user_service.user_crud.create_user")
@patch("app.services.user_service.user_crud.get_user_by_nickname")
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_register_user_service_success(
    mock_get_by_email,
    mock_get_by_nickname,
    mock_create_user,
    mock_hash,
    mock_create_token,
):
    mock_db = Mock()
    new_user = Mock(id=42)

    mock_get_by_email.return_value = None
    mock_get_by_nickname.return_value = None
    mock_hash.return_value = "hash"
    mock_create_user.return_value = new_user
    mock_create_token.return_value = "test_token"

    result = register_user_service(mock_db, "test@test.com", "Test", "pass")

    mock_get_by_email.assert_called_once_with(mock_db, "test@test.com")
    mock_get_by_nickname.assert_called_once_with(mock_db, "Test")
    mock_hash.assert_called_once_with("pass")
    mock_create_user.assert_called_once_with(
        data_base=mock_db,
        email="test@test.com",
        nickname="Test",
        password_hash="hash",
    )
    mock_create_token.assert_called_once_with({"sub": str(new_user.id)})
    assert result == {"access_token": "test_token", "token_type": "Bearer"}


@patch("app.services.user_service.user_crud.get_user_by_email")
def test_register_user_service_email_conflict(mock_get_by_email):
    mock_db = Mock()

    mock_get_by_email.return_value = Mock(id=42)

    with pytest.raises(exception.ConflictError):
        register_user_service(mock_db, "test@test.com", "Test", "pass")


@patch("app.services.user_service.user_crud.get_user_by_nickname")
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_register_user_service_nickname_conflict(
    mock_get_by_email, mock_get_by_nickname
):
    mock_db = Mock()

    mock_get_by_email.return_value = None
    mock_get_by_nickname.return_value = Mock(id=42)

    with pytest.raises(exception.ConflictError):
        register_user_service(mock_db, "test@test.com", "Test", "pass")


@patch("app.services.user_service.security.get_password_hash")
@patch("app.services.user_service.user_crud.create_user")
@patch("app.services.user_service.user_crud.get_user_by_nickname")
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_register_user_service_create_conflict(
    mock_get_by_email, mock_get_by_nickname, mock_create_user, mock_hash
):
    mock_db = Mock()

    mock_get_by_email.return_value = None
    mock_get_by_nickname.return_value = None
    mock_hash.return_value = "hash"
    mock_create_user.side_effect = exception.ConflictError()

    with pytest.raises(exception.ConflictError):
        register_user_service(mock_db, "test@test.com", "Test ", "pass")


@patch("app.services.user_service.security.create_access_token")
@patch("app.services.user_service.security.verify_password")
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_login_user_service_success(mock_get_by_email, mock_verify, mock_create_token):
    mock_db = Mock()
    user_obj = Mock(id=42, password_hash="hash")

    mock_get_by_email.return_value = user_obj
    mock_verify.return_value = True
    mock_create_token.return_value = "test_token"

    result = login_user_service(mock_db, "test@test.com", "pass")

    mock_get_by_email.assert_called_once_with(mock_db, "test@test.com")
    mock_verify.assert_called_once_with("pass", "hash")
    mock_create_token.assert_called_once_with({"sub": str(user_obj.id)})
    assert result == {"access_token": "test_token", "token_type": "Bearer"}


@patch("app.services.user_service.user_crud.get_user_by_email")
def test_login_user_service_user_not_found(mock_get_by_email):
    mock_db = Mock()

    mock_get_by_email.return_value = None

    with pytest.raises(exception.ForbiddenError):
        login_user_service(mock_db, "test@test.com", "pass")


@patch("app.services.user_service.security.verify_password")
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_login_user_service_wrong_password(mock_get_by_email, mock_verify):
    mock_db = Mock()
    user_obj = Mock(id=42, password_hash="hash")

    mock_get_by_email.return_value = user_obj
    mock_verify.return_value = False

    with pytest.raises(exception.ForbiddenError):
        login_user_service(mock_db, "test@test.com", "pass")


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_by_token_service_success(mock_get_user, mock_get_teams):
    mock_db = Mock()
    user_id = 42
    user_obj = Mock(id=user_id)
    teams = [Mock(), Mock()]

    mock_get_user.return_value = user_obj
    mock_get_teams.return_value = teams

    result_user, result_teams = get_user_by_token_service(mock_db, user_id)

    mock_get_user.assert_called_once_with(mock_db, user_id)
    mock_get_teams.assert_called_once_with(mock_db, user_obj.id)
    assert result_user is user_obj
    assert result_teams is teams


@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_by_token_service_user_not_found(mock_get_user):
    mock_db = Mock()
    user_id = 42

    mock_get_user.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_user_by_token_service(mock_db, user_id)


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_service_success(mock_get_user, mock_get_teams):
    mock_db = Mock()
    user_id = 42
    user_obj = Mock(id=user_id)
    teams = [Mock(), Mock()]

    mock_get_user.return_value = user_obj
    mock_get_teams.return_value = teams

    result_user, result_teams = get_user_service(mock_db, user_id, user_id)

    mock_get_user.assert_called_once_with(mock_db, user_id)
    mock_get_teams.assert_called_once_with(mock_db, user_id)
    assert result_user is user_obj
    assert result_teams is teams


def test_get_user_service_forbidden_different_user():
    mock_db = Mock()
    requested_user_id = 42
    current_user_id = 43

    with pytest.raises(exception.ForbiddenError):
        get_user_service(mock_db, requested_user_id, current_user_id)


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_service_user_not_found(mock_get_user, mock_get_teams):
    mock_db = Mock()
    user_id = 42

    mock_get_user.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_user_service(mock_db, user_id, user_id)

    mock_get_teams.assert_not_called()
