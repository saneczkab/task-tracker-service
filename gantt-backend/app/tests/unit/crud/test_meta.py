from unittest.mock import Mock

from app.crud.meta import get_team_statuses, get_team_priorities, get_connection_types


def test_get_team_statuses_returns_list():
    mock_db = Mock()
    expected = [Mock(), Mock()]
    mock_db.query.return_value.all.return_value = expected

    result = get_team_statuses(mock_db)

    assert result == expected
    mock_db.query.return_value.all.assert_called_once()


def test_get_team_statuses_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.all.return_value = []

    result = get_team_statuses(mock_db)

    assert result == []


def test_get_team_priorities_returns_list():
    mock_db = Mock()
    expected = [Mock(), Mock(), Mock()]
    mock_db.query.return_value.all.return_value = expected

    result = get_team_priorities(mock_db)

    assert result == expected
    mock_db.query.return_value.all.assert_called_once()


def test_get_team_priorities_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.all.return_value = []

    result = get_team_priorities(mock_db)

    assert result == []


def test_get_connection_types_returns_list():
    mock_db = Mock()
    expected = [Mock()]
    mock_db.query.return_value.all.return_value = expected

    result = get_connection_types(mock_db)

    assert result == expected
    mock_db.query.return_value.all.assert_called_once()


def test_get_connection_types_returns_empty_list():
    mock_db = Mock()
    mock_db.query.return_value.all.return_value = []

    result = get_connection_types(mock_db)

    assert result == []
