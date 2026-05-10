from app.crud.team import (
    add_user_to_team,
    create_team,
    delete_member,
    delete_team,
    get_team_by_id,
    get_team_users,
    get_teams_by_user,
    get_user_by_email,
    get_user_team,
    get_user_team_by_id,
)
from app.models import team as team_model


def test_get_user_team_by_id_returns_user_team(db_session, user_team_obj):
    result = get_user_team_by_id(db_session, user_id=42, team_id=42)
    assert result.id == user_team_obj.id


def test_get_user_team_by_id_returns_none_when_not_found(db_session):
    result = get_user_team_by_id(db_session, user_id=42, team_id=42)
    assert result is None


def test_get_team_by_id_returns_team(db_session, team_obj):
    result = get_team_by_id(db_session, team_id=42)
    assert result.id == team_obj.id


def test_get_team_by_id_returns_none_when_not_found(db_session):
    result = get_team_by_id(db_session, team_id=42)
    assert result is None


def test_get_user_team_returns_user_team(db_session, user_team_obj):
    result = get_user_team(db_session, team_id=42, user_id=42)
    assert result.id == user_team_obj.id


def test_get_user_team_returns_none_when_not_found(db_session):
    result = get_user_team(db_session, team_id=42, user_id=42)
    assert result is None


def test_get_team_users_returns_list(db_session, user_team_obj):
    result = get_team_users(db_session, team_id=42)
    assert len(result) == 1
    assert result[0].id == user_team_obj.id


def test_get_team_users_returns_empty_list(db_session):
    result = get_team_users(db_session, team_id=42)
    assert result == []


def test_get_teams_by_user_returns_list(db_session, user_team_obj):
    result = get_teams_by_user(db_session, user_id=42)
    assert len(result) == 1
    assert result[0].id == 42


def test_get_teams_by_user_returns_empty_list(db_session):
    result = get_teams_by_user(db_session, user_id=42)
    assert result == []


def test_get_user_by_email_returns_user(db_session, user_obj):
    result = get_user_by_email(db_session, email=user_obj.email)
    assert result.id == user_obj.id


def test_get_user_by_email_returns_none_when_not_found(db_session):
    result = get_user_by_email(db_session, email="not-exists@test.com")
    assert result is None


def test_create_team(db_session):
    result = create_team(db_session, name="Test")
    assert result.name == "Test"
    assert result.id is not None


def test_add_user_to_team(db_session, role_editor, user_obj, team_obj):
    result = add_user_to_team(db_session, team_obj.id, user_obj.id, role_editor.id)
    assert result.team_id == team_obj.id
    assert result.user_id == user_obj.id
    assert result.role_id == role_editor.id


def test_delete_member_calls_delete_and_commit(db_session, user_team_obj):
    delete_member(db_session, team_id=42, user_id=42)
    assert get_user_team(db_session, team_id=42, user_id=42) is None


def test_delete_member_does_not_break_other_members(
    db_session, role_editor, user_obj, second_user_obj, team_obj
):
    first = add_user_to_team(db_session, team_obj.id, user_obj.id, role_editor.id)
    second = add_user_to_team(
        db_session, team_obj.id, second_user_obj.id, role_editor.id
    )
    first_id = first.id
    second_id = second.id

    delete_member(db_session, team_id=team_obj.id, user_id=user_obj.id)

    left = (
        db_session.query(team_model.UserTeam)
        .filter(team_model.UserTeam.id == second_id)
        .first()
    )
    removed = (
        db_session.query(team_model.UserTeam)
        .filter(team_model.UserTeam.id == first_id)
        .first()
    )
    assert left is not None
    assert removed is None


def test_delete_team_calls_delete_and_commit(db_session, team_obj):
    delete_team(db_session, team_obj)
    assert get_team_by_id(db_session, team_id=42) is None


def test_delete_team_does_not_refresh(db_session):
    team = create_team(db_session, name="Tmp")
    delete_team(db_session, team)
    assert get_team_by_id(db_session, team.id) is None
