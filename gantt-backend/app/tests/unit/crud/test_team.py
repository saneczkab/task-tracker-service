from unittest.mock import Mock

from app.crud.team import (
    get_user_team_by_id,
    get_team_by_id,
    get_user_team,
    get_team_users,
    get_teams_by_user,
    get_user_by_email,
    create_team,
    add_user_to_team,
    delete_member,
    delete_team,
)


def test_get_user_team_by_id_returns_user_team():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_user_team_by_id(mock_db, user_id=42, team_id=42)

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_user_team_by_id_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_user_team_by_id(mock_db, user_id=42, team_id=42)

    assert result is None


def test_get_team_by_id_returns_team():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_team_by_id(mock_db, team_id=42)

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_team_by_id_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_team_by_id(mock_db, team_id=42)

    assert result is None


def test_get_user_team_returns_user_team():
    mock_db = Mock()
    expected = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = get_user_team(mock_db, team_id=42, user_id=42)

    assert result is expected
    mock_db.query.return_value.filter.return_value.first.assert_called_once()


def test_get_user_team_returns_none_when_not_found():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = get_user_team(mock_db, team_id=42, user_id=42)

    assert result is None


def test_get_team_users_returns_list():
    mock_db = Mock()
    expected = [Mock(), Mock()]
    mock_db.query.return_value.filter.return_value.all.return_value = expected

    result = get_team_users(mock_db, team_id=42)

    assert result == expected
    mock_db.query.return_value.filter.return_value.all.assert_called_once()


def test_get_team_users_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    result = get_team_users(mock_db, team_id=42)

    assert result == []


def test_get_teams_by_user_returns_list():
    mock_db = Mock()
    expected = [Mock(), Mock()]
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = expected

    result = get_teams_by_user(mock_db, user_id=42)

    assert result == expected
    mock_db.query.return_value.join.return_value.filter.return_value.all.assert_called_once()


def test_get_teams_by_user_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []

    result = get_teams_by_user(mock_db, user_id=42)

    assert result == []


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

    result = get_user_by_email(mock_db, email="not-exists@test.com")

    assert result is None


def test_create_team():
    mock_db = Mock()

    result = create_team(mock_db, name="Test")

    assert result.name == "Test"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


def test_add_user_to_team():
    mock_db = Mock()
    team_id = 42
    user_id = 42
    role_id = 1

    result = add_user_to_team(mock_db, team_id, user_id, role_id)

    assert result.team_id == team_id
    assert result.user_id == user_id
    assert result.role_id == role_id

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    added_obj = mock_db.add.call_args[0][0]
    mock_db.refresh.assert_called_once_with(added_obj)
    assert result is added_obj


def test_delete_member_calls_delete_and_commit():
    mock_db = Mock()

    delete_member(mock_db, team_id=42, user_id=42)

    mock_db.query.return_value.filter.return_value.delete.assert_called_once()
    mock_db.commit.assert_called_once()


def test_delete_member_does_not_refresh():
    mock_db = Mock()

    delete_member(mock_db, team_id=42, user_id=42)

    mock_db.refresh.assert_not_called()


def test_delete_team_calls_delete_and_commit():
    mock_db = Mock()
    team_obj = Mock()

    delete_team(mock_db, team_obj)

    mock_db.delete.assert_called_once_with(team_obj)
    mock_db.commit.assert_called_once()


def test_delete_team_does_not_refresh():
    mock_db = Mock()
    team_obj = Mock()

    delete_team(mock_db, team_obj)

    mock_db.refresh.assert_not_called()
