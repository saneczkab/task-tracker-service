from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.services.user_service import (
    check_email_exists_service,
    get_current_user_service,
    get_user_by_token_service,
    get_user_service,
    login_user_service,
    register_user_service,
)


@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_current_user_service_success(mock_get_user_by_id, mock_db, ids, mock_user):
    mock_get_user_by_id.return_value = mock_user

    result = get_current_user_service(mock_db, ids.user_id)

    mock_get_user_by_id.assert_called_once_with(mock_db, ids.user_id)
    assert result is mock_user


@pytest.mark.parametrize("crud_result, expected", [(object(), True), (None, False)])
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_check_email_exists_service(
    mock_get_user_by_email, mock_db, crud_result, expected
):
    email = "test@test.com"
    mock_get_user_by_email.return_value = crud_result

    result = check_email_exists_service(mock_db, email)

    mock_get_user_by_email.assert_called_once_with(mock_db, email)
    assert result is expected


@patch.multiple(
    "app.services.user_service.security",
    get_password_hash=DEFAULT,
    create_access_token=DEFAULT,
)
@patch.multiple(
    "app.services.user_service.user_crud",
    get_user_by_email=DEFAULT,
    get_user_by_nickname=DEFAULT,
    create_user=DEFAULT,
)
def test_register_user_service_success(
    mock_db,
    **mocks,
):
    email = "test@test.com"
    nickname = "Test"
    password = "pass"
    new_user = Mock(id=1001)
    expected_token = "test_token"

    mocks["get_user_by_email"].return_value = None
    mocks["get_user_by_nickname"].return_value = None
    mocks["create_user"].return_value = new_user
    mocks["get_password_hash"].return_value = "hash"
    mocks["create_access_token"].return_value = expected_token

    result = register_user_service(mock_db, email, nickname, password)

    mocks["get_password_hash"].assert_called_once_with(password)
    mocks["create_user"].assert_called_once_with(
        data_base=mock_db,
        email=email,
        nickname=nickname,
        password_hash="hash",
    )
    mocks["create_access_token"].assert_called_once_with({"sub": str(new_user.id)})
    assert result == {"access_token": expected_token, "token_type": "Bearer"}


@patch("app.services.user_service.user_crud.get_user_by_email")
def test_register_user_service_email_conflict(mock_get_user_by_email, mock_db):
    existing_user = Mock(id=1002)
    mock_get_user_by_email.return_value = existing_user

    with pytest.raises(exception.ConflictError):
        register_user_service(mock_db, "test@test.com", "Test", "pass")


@patch.multiple(
    "app.services.user_service.security",
    create_access_token=DEFAULT,
    verify_password=DEFAULT,
)
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_login_user_service_success(
    mock_get_user_by_email,
    mock_db,
    **mocks,
):
    email = "test@test.com"
    user_obj = Mock(id=1003, password_hash="hash")
    expected_token = "token"
    mock_get_user_by_email.return_value = user_obj
    mocks["verify_password"].return_value = True
    mocks["create_access_token"].return_value = expected_token

    result = login_user_service(mock_db, email, "pass")

    mock_get_user_by_email.assert_called_once_with(mock_db, email)
    mocks["verify_password"].assert_called_once_with("pass", user_obj.password_hash)
    mocks["create_access_token"].assert_called_once_with({"sub": str(user_obj.id)})
    assert result == {"access_token": expected_token, "token_type": "Bearer"}


@patch("app.services.user_service.user_crud.get_user_by_email")
def test_login_user_service_forbidden_when_invalid_credentials(
    mock_get_user_by_email, mock_db
):
    mock_get_user_by_email.return_value = None

    with pytest.raises(exception.ForbiddenError):
        login_user_service(mock_db, "test@test.com", "pass")


@patch.multiple(
    "app.services.user_service.security",
    create_access_token=DEFAULT,
    verify_password=DEFAULT,
)
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_login_user_service_forbidden_when_wrong_password(
    mock_get_user_by_email,
    mock_db,
    **mocks,
):
    user_obj = Mock(id=1005, password_hash="hash")
    mock_get_user_by_email.return_value = user_obj
    mocks["verify_password"].return_value = False

    with pytest.raises(exception.ForbiddenError):
        login_user_service(mock_db, "test@test.com", "pass")

    mocks["verify_password"].assert_called_once_with("pass", user_obj.password_hash)
    mocks["create_access_token"].assert_not_called()


@patch("app.services.user_service.user_crud.get_user_by_nickname")
@patch("app.services.user_service.user_crud.get_user_by_email")
def test_register_user_service_nickname_conflict(
    mock_get_user_by_email,
    mock_get_user_by_nickname,
    mock_db,
):
    mock_get_user_by_email.return_value = None
    mock_get_user_by_nickname.return_value = Mock(id=1004)

    with pytest.raises(exception.ConflictError, match="Никнейм уже используется"):
        register_user_service(mock_db, "test@test.com", "Test", "pass")


@patch.multiple(
    "app.services.user_service.security",
    get_password_hash=DEFAULT,
)
@patch.multiple(
    "app.services.user_service.user_crud",
    get_user_by_email=DEFAULT,
    get_user_by_nickname=DEFAULT,
    create_user=DEFAULT,
)
def test_register_user_service_create_user_conflict(mock_db, **mocks):
    mocks["get_user_by_email"].return_value = None
    mocks["get_user_by_nickname"].return_value = None
    mocks["get_password_hash"].return_value = "hash"
    mocks["create_user"].side_effect = exception.ConflictError()

    with pytest.raises(
        exception.ConflictError, match="Email или никнейм уже используются"
    ):
        register_user_service(mock_db, "test@test.com", "Test", "pass")


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_by_token_service_success(
    mock_get_user_by_id, mock_get_teams_by_user, mock_db, ids, mock_user
):
    expected_teams = [Mock(), Mock()]
    mock_get_user_by_id.return_value = mock_user
    mock_get_teams_by_user.return_value = expected_teams

    result_user, result_teams = get_user_by_token_service(mock_db, ids.user_id)

    mock_get_user_by_id.assert_called_once_with(mock_db, ids.user_id)
    mock_get_teams_by_user.assert_called_once_with(mock_db, mock_user.id)
    assert result_user is mock_user
    assert result_teams is expected_teams


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_by_token_service_not_found(
    mock_get_user_by_id, mock_get_teams_by_user, mock_db, ids
):
    mock_get_user_by_id.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_user_by_token_service(mock_db, ids.user_id)

    mock_get_teams_by_user.assert_not_called()


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_service_success(
    mock_get_user_by_id, mock_get_teams_by_user, mock_db, ids, mock_user
):
    expected_teams = [Mock()]
    mock_get_user_by_id.return_value = mock_user
    mock_get_teams_by_user.return_value = expected_teams

    result_user, result_teams = get_user_service(mock_db, ids.user_id, ids.user_id)

    mock_get_user_by_id.assert_called_once_with(mock_db, ids.user_id)
    mock_get_teams_by_user.assert_called_once_with(mock_db, ids.user_id)
    assert result_user is mock_user
    assert result_teams is expected_teams


@patch("app.services.user_service.team_crud.get_teams_by_user")
@patch("app.services.user_service.user_crud.get_user_by_id")
def test_get_user_service_not_found(
    mock_get_user_by_id, mock_get_teams_by_user, mock_db, ids
):
    mock_get_user_by_id.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_user_service(mock_db, ids.user_id, ids.user_id)

    mock_get_teams_by_user.assert_not_called()


def test_get_user_service_forbidden_different_user(mock_db, ids):
    with pytest.raises(exception.ForbiddenError):
        get_user_service(mock_db, ids.user_id, ids.second_user_id)
