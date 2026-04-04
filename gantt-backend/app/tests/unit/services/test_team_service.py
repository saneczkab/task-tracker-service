from unittest.mock import Mock, patch, call

import pytest

from app.core import exception
from app.models.role import Role
from app.services.team_service import (
    check_team_permissions,
    get_team_users_service,
    create_team_service,
    update_team_service,
    delete_team_service,
)


@patch("app.services.team_service.team_crud.get_user_team")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_check_team_permissions_success(mock_get_team, mock_get_user_team):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    member = Mock(role_id=Role.READER)

    mock_get_team.return_value = team_obj
    mock_get_user_team.return_value = member

    result = check_team_permissions(mock_db, team_id, user_id)

    mock_get_team.assert_called_once_with(mock_db, team_id)
    mock_get_user_team.assert_called_once_with(mock_db, team_id, user_id)
    assert result is member


@patch("app.services.team_service.team_crud.get_user_team")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_check_team_permissions_need_lead_success(mock_get_team, mock_get_user_team):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    member = Mock(role_id=Role.EDITOR)

    mock_get_team.return_value = team_obj
    mock_get_user_team.return_value = member

    result = check_team_permissions(mock_db, team_id, user_id, need_lead=True)

    assert result is member


@patch("app.services.team_service.team_crud.get_team_by_id")
def test_check_team_permissions_team_not_found(mock_get_team):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_get_team.return_value = None

    with pytest.raises(exception.NotFoundError):
        check_team_permissions(mock_db, team_id, user_id)


@patch("app.services.team_service.team_crud.get_user_team")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_check_team_permissions_user_not_in_team(mock_get_team, mock_get_user_team):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)

    mock_get_team.return_value = team_obj
    mock_get_user_team.return_value = None

    with pytest.raises(exception.ForbiddenError):
        check_team_permissions(mock_db, team_id, user_id)


@patch("app.services.team_service.team_crud.get_user_team")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_check_team_permissions_need_lead_but_not_editor(
    mock_get_team, mock_get_user_team
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    member = Mock(role_id=Role.READER)

    mock_get_team.return_value = team_obj
    mock_get_user_team.return_value = member

    with pytest.raises(exception.ForbiddenError):
        check_team_permissions(mock_db, team_id, user_id, need_lead=True)


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_users")
def test_get_team_users_service_success(mock_get_users, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    editor_member = Mock()
    editor_member.user.id = 42
    editor_member.user.email = "test@test.com"
    editor_member.user.nickname = "Test"
    editor_member.role_id = Role.EDITOR

    reader_member = Mock()
    reader_member.user.id = 43
    reader_member.user.email = "test2@test.com"
    reader_member.user.nickname = "Test2"
    reader_member.role_id = Role.READER

    mock_check_perms.return_value = Mock()
    mock_get_users.return_value = [editor_member, reader_member]

    result = get_team_users_service(mock_db, team_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, team_id, user_id)
    mock_get_users.assert_called_once_with(mock_db, team_id)
    assert len(result) == 2
    assert result[0] == {
        "id": 42,
        "email": "test@test.com",
        "nickname": "Test",
        "role": "Editor",
    }
    assert result[1] == {
        "id": 43,
        "email": "test2@test.com",
        "nickname": "Test2",
        "role": "Reader",
    }


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_users")
def test_get_team_users_service_team_not_found(mock_get_users, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_team_users_service(mock_db, team_id, user_id)

    mock_get_users.assert_not_called()


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_users")
def test_get_team_users_service_forbidden(mock_get_users, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_team_users_service(mock_db, team_id, user_id)

    mock_get_users.assert_not_called()


@patch("app.services.team_service.team_crud.add_user_to_team")
@patch("app.services.team_service.team_crud.create_team")
def test_create_team_service_success(mock_create_team, mock_add_user):
    mock_db = Mock()
    owner_id = 42
    create_data = Mock()
    create_data.name = "Test team"
    team_obj = Mock(id=42)

    mock_create_team.return_value = team_obj

    result = create_team_service(mock_db, owner_id, create_data)

    mock_create_team.assert_called_once_with(mock_db, "Test team")
    mock_add_user.assert_called_once_with(mock_db, team_obj.id, owner_id, Role.EDITOR)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(team_obj)
    assert result is team_obj


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_success_name_only(mock_get_team, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    update_data = Mock()
    update_data.name = "Test team"
    update_data.newUsers = None
    update_data.deleteUsers = None

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()

    result = update_team_service(mock_db, team_id, user_id, update_data)

    mock_get_team.assert_called_once_with(mock_db, team_id)
    mock_check_perms.assert_called_once_with(mock_db, team_id, user_id, need_lead=True)
    assert team_obj.name == "Test team"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(team_obj)
    assert result is team_obj


@patch("app.services.team_service.team_crud.add_user_to_team")
@patch("app.services.team_service.team_crud.get_user_team")
@patch("app.services.team_service.team_crud.get_user_by_email")
@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_add_new_users(
    mock_get_team,
    mock_check_perms,
    mock_get_user_by_email,
    mock_get_user_team,
    mock_add_user,
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    new_user = Mock(id=43)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = ["test@test.com"]
    update_data.deleteUsers = None

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_get_user_by_email.return_value = new_user
    mock_get_user_team.return_value = None

    update_team_service(mock_db, team_id, user_id, update_data)

    mock_add_user.assert_called_once_with(mock_db, team_id, new_user.id, Role.READER)


@patch("app.services.team_service.team_crud.add_user_to_team")
@patch("app.services.team_service.team_crud.get_user_team")
@patch("app.services.team_service.team_crud.get_user_by_email")
@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_skip_existing_user(
    mock_get_team,
    mock_check_perms,
    mock_get_user_by_email,
    mock_get_user_team,
    mock_add_user,
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    existing_user = Mock(id=43)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = ["test@test.com"]
    update_data.deleteUsers = None

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_get_user_by_email.return_value = existing_user
    mock_get_user_team.return_value = Mock()

    update_team_service(mock_db, team_id, user_id, update_data)

    mock_add_user.assert_not_called()


@patch("app.services.team_service.team_crud.get_user_by_email")
@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_new_user_not_found(
    mock_get_team, mock_check_perms, mock_get_user_by_email
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = ["not-exists@test.com"]
    update_data.deleteUsers = None

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_get_user_by_email.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_team_service(mock_db, team_id, user_id, update_data)


@patch("app.services.team_service.team_crud.get_user_by_email")
@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_delete_users(
    mock_get_team, mock_check_perms, mock_get_user_by_email
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    delete_user = Mock(id=43)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = None
    update_data.deleteUsers = ["test@test.com"]

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_get_user_by_email.return_value = delete_user

    with patch(
        "app.services.team_service.team_crud.delete_user_from_team", create=True
    ) as mock_delete_user:
        update_team_service(mock_db, team_id, user_id, update_data)
        mock_delete_user.assert_called_once_with(mock_db, team_id, delete_user.id)


@patch("app.services.team_service.team_crud.get_user_by_email")
@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_delete_user_not_found(
    mock_get_team, mock_check_perms, mock_get_user_by_email
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = None
    update_data.deleteUsers = ["not-exists@test.com"]

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_get_user_by_email.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_team_service(mock_db, team_id, user_id, update_data)


@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_team_not_found(mock_get_team):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    update_data = Mock()

    mock_get_team.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_team_service(mock_db, team_id, user_id, update_data)


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_forbidden(mock_get_team, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    update_data = Mock()

    mock_get_team.return_value = team_obj
    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        update_team_service(mock_db, team_id, user_id, update_data)


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_success_no_projects(mock_get_team, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_db.query.return_value.filter_by.return_value.all.return_value = []

    delete_team_service(mock_db, team_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, team_id, user_id, need_lead=True)
    mock_db.delete.assert_called_once_with(team_obj)
    mock_db.commit.assert_called_once()


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_success_with_projects_streams_tasks(
    mock_get_team, mock_check_perms
):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)
    project_obj = Mock(id=42)
    stream_obj = Mock(id=42)

    mock_get_team.return_value = team_obj
    mock_check_perms.return_value = Mock()
    mock_db.query.return_value.filter_by.return_value.all.return_value = [project_obj]
    mock_db.query.return_value.filter.return_value.all.return_value = [stream_obj]
    mock_db.query.return_value.filter.return_value.delete.return_value = None

    delete_team_service(mock_db, team_id, user_id)

    mock_db.delete.assert_called_once_with(team_obj)
    mock_db.commit.assert_called_once()


@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_team_not_found(mock_get_team):
    mock_db = Mock()
    team_id = 42
    user_id = 42

    mock_get_team.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_team_service(mock_db, team_id, user_id)


@patch("app.services.team_service.check_team_permissions")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_forbidden(mock_get_team, mock_check_perms):
    mock_db = Mock()
    team_id = 42
    user_id = 42
    team_obj = Mock(id=team_id)

    mock_get_team.return_value = team_obj
    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_team_service(mock_db, team_id, user_id)

    mock_db.delete.assert_not_called()
