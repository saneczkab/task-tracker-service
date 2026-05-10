from app.crud.meta import get_team_statuses, get_team_priorities, get_connection_types


def test_get_team_statuses_returns_list(db_session, status_obj):
    result = get_team_statuses(db_session)
    assert len(result) == 1
    assert result[0].id == status_obj.id


def test_get_team_statuses_returns_empty_list(db_session):
    result = get_team_statuses(db_session)

    assert result == []


def test_get_team_priorities_returns_list(db_session, priority_obj):
    result = get_team_priorities(db_session)
    assert len(result) == 1
    assert result[0].id == priority_obj.id


def test_get_team_priorities_returns_empty_list(db_session):
    result = get_team_priorities(db_session)

    assert result == []


def test_get_connection_types_returns_list(db_session, connection_type_obj):
    result = get_connection_types(db_session)
    assert len(result) == 1
    assert result[0].id == connection_type_obj.id


def test_get_connection_types_returns_empty_list(db_session):
    result = get_connection_types(db_session)

    assert result == []
