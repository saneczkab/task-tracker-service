from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.models import goal as goal_model
from app.models import project as project_model
from app.models import stream as stream_model
from app.models import task as task_model
from app.models import team as team_model
from app.models.role import Role
from app.services.team_service import (
    create_team_service,
    delete_team_service,
    get_team_users_service,
    update_team_service,
)


@patch("app.services.team_service.team_crud.get_team_users")
@patch("app.services.team_service.permissions.check_team_access")
def test_get_team_users_service_success(
    mock_check_team_access, mock_get_team_users, mock_db, ids, make_team_member
):
    editor_member = make_team_member(
        ids.user_id, "editor@test.com", "Editor", role_id=Role.EDITOR
    )
    reader_member = make_team_member(
        ids.second_user_id, "reader@test.com", "Reader", role_id=Role.READER
    )
    expected = [
        {
            "id": editor_member.user.id,
            "email": editor_member.user.email,
            "nickname": editor_member.user.nickname,
            "role": "Editor",
        },
        {
            "id": reader_member.user.id,
            "email": reader_member.user.email,
            "nickname": reader_member.user.nickname,
            "role": "Reader",
        },
    ]

    mock_get_team_users.return_value = [editor_member, reader_member]

    result = get_team_users_service(mock_db, ids.team_id, ids.user_id)

    mock_check_team_access.assert_called_once_with(mock_db, ids.team_id, ids.user_id)
    mock_get_team_users.assert_called_once_with(mock_db, ids.team_id)
    assert result == expected


@patch("app.services.team_service.team_crud.get_team_users")
@patch("app.services.team_service.permissions.check_team_access")
def test_get_team_users_service_forbidden(
    mock_check_team_access, mock_get_team_users, mock_db, ids
):
    mock_check_team_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_team_users_service(mock_db, ids.team_id, ids.user_id)

    mock_get_team_users.assert_not_called()


@patch.multiple(
    "app.services.team_service.team_crud",
    add_user_to_team=DEFAULT,
    create_team=DEFAULT,
)
def test_create_team_service_success(mock_db, ids, **mocks):
    create_data = Mock(name="Platform Team")
    mocks["create_team"].return_value = Mock(id=ids.team_id)

    result = create_team_service(mock_db, ids.user_id, create_data)

    mocks["create_team"].assert_called_once_with(mock_db, create_data.name)
    mocks["add_user_to_team"].assert_called_once_with(
        mock_db,
        mocks["create_team"].return_value.id,
        ids.user_id,
        Role.EDITOR,
    )
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mocks["create_team"].return_value)
    assert result is mocks["create_team"].return_value


@patch("app.services.team_service.permissions.check_team_access")
@patch.multiple(
    "app.services.team_service.team_crud",
    get_team_by_id=DEFAULT,
    get_user_by_email=DEFAULT,
    get_user_team=DEFAULT,
    add_user_to_team=DEFAULT,
    delete_user_from_team=DEFAULT,
    create=True,
)
def test_update_team_service_success_add_and_delete_users(
    mock_check_team_access,
    mock_db,
    ids,
    mock_team,
    mock_second_user,
    mock_user,
    **mocks,
):
    team_obj = mock_team
    team_obj.name = "Old"
    update_data = Mock(
        name="New",
        newUsers=["new@test.com"],
        deleteUsers=["old@test.com"],
    )
    added_user = mock_second_user
    removed_user = mock_user
    mocks["get_team_by_id"].return_value = team_obj
    mocks["get_user_by_email"].side_effect = [added_user, removed_user]
    mocks["get_user_team"].return_value = None

    result = update_team_service(mock_db, ids.team_id, ids.user_id, update_data)

    mock_check_team_access.assert_called_once_with(
        mock_db, ids.team_id, ids.user_id, need_lead=True
    )
    assert team_obj.name == update_data.name
    mocks["add_user_to_team"].assert_called_once_with(
        mock_db,
        ids.team_id,
        added_user.id,
        Role.READER,
    )
    mocks["delete_user_from_team"].assert_called_once_with(
        mock_db,
        ids.team_id,
        removed_user.id,
    )
    assert mocks["get_user_by_email"].call_count == len(update_data.newUsers) + len(
        update_data.deleteUsers
    )
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(team_obj)
    assert result is team_obj


@patch("app.services.team_service.permissions.check_team_access")
@patch.multiple(
    "app.services.team_service.team_crud",
    get_team_by_id=DEFAULT,
    get_user_by_email=DEFAULT,
    get_user_team=DEFAULT,
    add_user_to_team=DEFAULT,
    create=True,
)
def test_update_team_service_existing_member_not_added(
    mock_check_team_access,
    mock_db,
    ids,
    mock_team,
    mock_second_user,
    **mocks,
):
    team_obj = mock_team
    team_obj.name = "Old"
    update_data = Mock(name=None, newUsers=["existing@test.com"], deleteUsers=None)
    existing_user = mock_second_user
    existing_member = Mock(id=999)

    mocks["get_team_by_id"].return_value = team_obj
    mocks["get_user_by_email"].return_value = existing_user
    mocks["get_user_team"].return_value = existing_member

    result = update_team_service(mock_db, ids.team_id, ids.user_id, update_data)

    mock_check_team_access.assert_called_once_with(
        mock_db, ids.team_id, ids.user_id, need_lead=True
    )
    mocks["add_user_to_team"].assert_not_called()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(team_obj)
    assert result is team_obj


@patch("app.services.team_service.permissions.check_team_access")
@patch.multiple(
    "app.services.team_service.team_crud",
    get_team_by_id=DEFAULT,
    get_user_by_email=DEFAULT,
)
def test_update_team_service_user_not_found(
    _mock_check_team_access,
    mock_db,
    ids,
    **mocks,
):
    team_obj = Mock(id=ids.team_id)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = ["missing@test.com"]
    update_data.deleteUsers = None
    mocks["get_team_by_id"].return_value = team_obj
    mocks["get_user_by_email"].return_value = None

    with pytest.raises(exception.NotFoundError):
        update_team_service(mock_db, ids.team_id, ids.user_id, update_data)


@patch("app.services.team_service.permissions.check_team_access")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_update_team_service_team_not_found(
    mock_get_team_by_id, mock_check_team_access, mock_db, ids
):
    mock_get_team_by_id.return_value = None
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = None
    update_data.deleteUsers = None

    with pytest.raises(exception.NotFoundError):
        update_team_service(mock_db, ids.team_id, ids.user_id, update_data)

    mock_check_team_access.assert_not_called()


@patch("app.services.team_service.permissions.check_team_access")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_success_without_projects(
    mock_get_team_by_id,
    mock_check_team_access,
    mock_db,
    ids,
    make_query_router,
    make_query,
):
    team_obj = Mock(id=ids.team_id)
    mock_get_team_by_id.return_value = team_obj

    q_projects = make_query(all_=[])
    q_userteam_delete = make_query()

    mock_db.query.side_effect = make_query_router(
        {
            project_model.Project: q_projects,
            team_model.UserTeam: q_userteam_delete,
        }
    )

    delete_team_service(mock_db, ids.team_id, ids.user_id)

    mock_check_team_access.assert_called_once_with(
        mock_db, ids.team_id, ids.user_id, need_lead=True
    )
    mock_db.delete.assert_called_once_with(team_obj)
    mock_db.commit.assert_called_once()


@patch("app.services.team_service.permissions.check_team_access")
@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_cascade_delete(
    mock_get_team_by_id,
    mock_check_team_access,
    mock_db,
    ids,
    make_query_router,
    make_query,
):
    team_obj = Mock(id=ids.team_id)
    project_obj = Mock(id=ids.project_id)
    stream_obj = Mock(id=ids.stream_id)

    mock_get_team_by_id.return_value = team_obj

    q_projects = make_query(all_=[project_obj])
    q_streams_all = make_query(all_=[stream_obj])
    q_task_delete = make_query()
    q_goal_delete = make_query()
    q_stream_delete = make_query()
    q_project_delete = make_query()
    q_userteam_delete = make_query()

    mock_db.query.side_effect = make_query_router(
        {
            project_model.Project: [q_projects, q_project_delete],
            stream_model.Stream: [q_streams_all, q_stream_delete],
            task_model.Task: q_task_delete,
            goal_model.Goal: q_goal_delete,
            team_model.UserTeam: q_userteam_delete,
        }
    )

    delete_team_service(mock_db, ids.team_id, ids.user_id)

    mock_check_team_access.assert_called_once_with(
        mock_db, ids.team_id, ids.user_id, need_lead=True
    )
    q_task_delete.delete.assert_called_once_with(synchronize_session=False)
    q_goal_delete.delete.assert_called_once_with(synchronize_session=False)
    q_stream_delete.delete.assert_called_once_with(synchronize_session=False)
    q_project_delete.delete.assert_called_once_with(synchronize_session=False)
    q_userteam_delete.delete.assert_called_once_with(synchronize_session=False)
    mock_db.delete.assert_called_once_with(team_obj)
    mock_db.commit.assert_called_once()


@patch("app.services.team_service.permissions.check_team_access")
@patch.multiple(
    "app.services.team_service.team_crud",
    get_team_by_id=DEFAULT,
    get_user_by_email=DEFAULT,
    delete_user_from_team=DEFAULT,
    create=True,
)
def test_update_team_service_delete_user_not_found(
    _mock_check_team_access,
    mock_db,
    ids,
    **mocks,
):
    team_obj = Mock(id=ids.team_id)
    update_data = Mock()
    update_data.name = None
    update_data.newUsers = None
    update_data.deleteUsers = ["missing@test.com"]
    mocks["get_team_by_id"].return_value = team_obj
    mocks["get_user_by_email"].return_value = None

    with pytest.raises(exception.NotFoundError):
        update_team_service(mock_db, ids.team_id, ids.user_id, update_data)

    mocks["delete_user_from_team"].assert_not_called()


@patch("app.services.team_service.team_crud.get_team_by_id")
def test_delete_team_service_not_found(mock_get_team_by_id, mock_db, ids):
    mock_get_team_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_team_service(mock_db, ids.team_id, ids.user_id)
