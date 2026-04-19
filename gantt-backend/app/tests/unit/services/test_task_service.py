from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.models.role import Role
from app.services.task_service import (
    check_task_permissions,
    get_project_tasks_service,
    get_stream_tasks_service,
    create_task_service,
    update_task_service,
    delete_task_service,
    create_task_relation_service,
)


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_check_task_permissions_success(mock_get_task):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id, stream_id=42)
    stream_obj = Mock(id=42, project_id=42)
    project_obj = Mock(id=42)
    project_obj.team.id = 42
    user_team = Mock(role_id=Role.READER)

    mock_get_task.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        stream_obj,
        project_obj,
        user_team,
    ]

    result = check_task_permissions(mock_db, task_id, user_id)

    assert result is task_obj


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_check_task_permissions_need_lead_success(mock_get_task):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id, stream_id=42)
    stream_obj = Mock(id=42, project_id=42)
    project_obj = Mock(id=42)
    project_obj.team.id = 42
    user_team = Mock(role_id=Role.EDITOR)

    mock_get_task.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        stream_obj,
        project_obj,
        user_team,
    ]

    result = check_task_permissions(mock_db, task_id, user_id, need_lead=True)

    assert result is task_obj


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_check_task_permissions_task_not_found(mock_get_task):
    mock_db = Mock()
    task_id = 42
    user_id = 42

    mock_get_task.return_value = None

    with pytest.raises(exception.NotFoundError):
        check_task_permissions(mock_db, task_id, user_id)


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_check_task_permissions_stream_not_found(mock_get_task):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id, stream_id=42)

    mock_get_task.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        check_task_permissions(mock_db, task_id, user_id)


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_check_task_permissions_user_not_in_team(mock_get_task):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id, stream_id=42)
    stream_obj = Mock(id=42, project_id=42)
    project_obj = Mock(id=42)
    project_obj.team.id = 42

    mock_get_task.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        stream_obj,
        project_obj,
        None,
    ]

    with pytest.raises(exception.ForbiddenError):
        check_task_permissions(mock_db, task_id, user_id)


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_check_task_permissions_need_lead_but_not_editor(mock_get_task):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id, stream_id=42)
    stream_obj = Mock(id=42, project_id=42)
    project_obj = Mock(id=42)
    project_obj.team.id = 42
    user_team = Mock(role_id=Role.READER)

    mock_get_task.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        stream_obj,
        project_obj,
        user_team,
    ]

    with pytest.raises(exception.ForbiddenError):
        check_task_permissions(mock_db, task_id, user_id, need_lead=True)


@patch("app.services.task_service.task_crud.get_tasks_by_project")
def test_get_project_tasks_service_success(mock_get_tasks):
    mock_db = Mock()
    project_id = 42
    user_id = 42
    project_obj = Mock(id=project_id)
    project_obj.team.id = 42
    user_team = Mock()
    mock_tasks = [Mock(), Mock()]

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        project_obj,
        user_team,
    ]
    mock_get_tasks.return_value = mock_tasks

    result = get_project_tasks_service(mock_db, project_id, user_id)

    mock_get_tasks.assert_called_once_with(mock_db, project_obj)
    assert result == mock_tasks


def test_get_project_tasks_service_project_not_found():
    mock_db = Mock()
    project_id = 42
    user_id = 42

    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        get_project_tasks_service(mock_db, project_id, user_id)


def test_get_project_tasks_service_forbidden():
    mock_db = Mock()
    project_id = 42
    user_id = 42
    project_obj = Mock(id=project_id)
    project_obj.team.id = 42

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        project_obj,
        None,
    ]

    with pytest.raises(exception.ForbiddenError):
        get_project_tasks_service(mock_db, project_id, user_id)


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.get_tasks_by_stream")
def test_get_stream_tasks_service_success(mock_get_tasks, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    mock_tasks = [Mock(), Mock()]

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_get_tasks.return_value = mock_tasks

    result = get_stream_tasks_service(mock_db, stream_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, stream_id, user_id)
    mock_get_tasks.assert_called_once_with(mock_db, stream_id)
    assert result == mock_tasks


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.get_tasks_by_stream")
def test_get_stream_tasks_service_stream_not_found(mock_get_tasks, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        get_stream_tasks_service(mock_db, stream_id, user_id)

    mock_get_tasks.assert_not_called()


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.get_tasks_by_stream")
def test_get_stream_tasks_service_forbidden(mock_get_tasks, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        get_stream_tasks_service(mock_db, stream_id, user_id)

    mock_get_tasks.assert_not_called()


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.create_task")
def test_create_task_service_success_with_position(mock_create, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    task_data = Mock()
    task_data.position = 2
    task_data.assignee_email = None
    expected_task = Mock()

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_create.return_value = expected_task

    result = create_task_service(mock_db, stream_id, user_id, task_data)

    mock_check_perms.assert_called_once_with(
        mock_db, stream_id, user_id, need_lead=True
    )
    mock_create.assert_called_once_with(mock_db, stream_id, task_data)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(expected_task)
    assert result is expected_task


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.create_task")
def test_create_task_service_auto_position_no_previous(mock_create, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    task_data = Mock()
    task_data.position = None
    task_data.assignee_email = None

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    mock_create.return_value = Mock()

    create_task_service(mock_db, stream_id, user_id, task_data)

    assert task_data.position == 1


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.create_task")
def test_create_task_service_auto_position_with_previous(mock_create, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    task_data = Mock()
    task_data.position = None
    task_data.assignee_email = None
    last_task = Mock(position=3)

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = last_task
    mock_create.return_value = Mock()

    create_task_service(mock_db, stream_id, user_id, task_data)

    assert task_data.position == 4


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.create_task")
def test_create_task_service_with_assignee(mock_create, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    task_data = Mock()
    task_data.position = 1
    task_data.assignee_email = "test@test.com"
    new_task = Mock(id=42)
    assignee = Mock(id=42)

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_create.return_value = new_task
    mock_db.query.return_value.filter.return_value.first.return_value = assignee

    create_task_service(mock_db, stream_id, user_id, task_data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(new_task)


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.create_task")
def test_create_task_service_assignee_not_found(mock_create, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    task_data = Mock()
    task_data.position = 1
    task_data.assignee_email = "not-exists@test.com"

    mock_check_perms.return_value = Mock(id=stream_id)
    mock_create.return_value = Mock(id=42)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        create_task_service(mock_db, stream_id, user_id, task_data)


@patch("app.services.task_service.check_stream_permissions")
@patch("app.services.task_service.task_crud.create_task")
def test_create_task_service_forbidden(mock_create, mock_check_perms):
    mock_db = Mock()
    stream_id = 42
    user_id = 42
    task_data = Mock()

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        create_task_service(mock_db, stream_id, user_id, task_data)

    mock_create.assert_not_called()


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.update_task")
def test_update_task_service_success_no_assignee(mock_update, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id)
    task_update_data = Mock()
    task_update_data.assignee_email = None

    mock_check_perms.return_value = task_obj

    result = update_task_service(mock_db, task_id, user_id, task_update_data)

    mock_check_perms.assert_called_once_with(mock_db, task_id, user_id, need_lead=True)
    mock_update.assert_called_once_with(mock_db, task_obj, task_update_data)
    assert result is task_obj


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.update_task")
def test_update_task_service_with_assignee_no_previous(mock_update, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id)
    task_update_data = Mock()
    task_update_data.assignee_email = "test@test.com"
    assignee = Mock(id=42)

    mock_check_perms.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.side_effect = [assignee, None]

    update_task_service(mock_db, task_id, user_id, task_update_data)

    mock_db.add.assert_called_once()
    mock_db.delete.assert_not_called()
    mock_update.assert_called_once_with(mock_db, task_obj, task_update_data)


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.update_task")
def test_update_task_service_with_assignee_replaces_previous(
    mock_update, mock_check_perms
):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id)
    task_update_data = Mock()
    task_update_data.assignee_email = "test@test.com"
    assignee = Mock(id=42)
    old_user_task = Mock()

    mock_check_perms.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        assignee,
        old_user_task,
    ]

    update_task_service(mock_db, task_id, user_id, task_update_data)

    mock_db.delete.assert_called_once_with(old_user_task)
    mock_db.add.assert_called_once()
    mock_update.assert_called_once_with(mock_db, task_obj, task_update_data)


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.update_task")
def test_update_task_service_assignee_not_found(mock_update, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id)
    task_update_data = Mock()
    task_update_data.assignee_email = "not-exists@test.com"

    mock_check_perms.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_task_service(mock_db, task_id, user_id, task_update_data)

    mock_update.assert_not_called()


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.update_task")
def test_update_task_service_task_not_found(mock_update, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_update_data = Mock()

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        update_task_service(mock_db, task_id, user_id, task_update_data)

    mock_update.assert_not_called()


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.update_task")
def test_update_task_service_forbidden(mock_update, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_update_data = Mock()

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        update_task_service(mock_db, task_id, user_id, task_update_data)

    mock_update.assert_not_called()


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.delete_task")
def test_delete_task_service_success_no_assignee(mock_delete, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id)

    mock_check_perms.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.return_value = None

    delete_task_service(mock_db, task_id, user_id)

    mock_check_perms.assert_called_once_with(mock_db, task_id, user_id, need_lead=True)
    mock_db.delete.assert_not_called()
    mock_delete.assert_called_once_with(mock_db, task_obj)


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.delete_task")
def test_delete_task_service_success_with_assignee(mock_delete, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42
    task_obj = Mock(id=task_id)
    old_user_task = Mock()

    mock_check_perms.return_value = task_obj
    mock_db.query.return_value.filter.return_value.first.return_value = old_user_task

    delete_task_service(mock_db, task_id, user_id)

    mock_db.delete.assert_called_once_with(old_user_task)
    mock_delete.assert_called_once_with(mock_db, task_obj)


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.delete_task")
def test_delete_task_service_task_not_found(mock_delete, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.NotFoundError()

    with pytest.raises(exception.NotFoundError):
        delete_task_service(mock_db, task_id, user_id)

    mock_delete.assert_not_called()


@patch("app.services.task_service.check_task_permissions")
@patch("app.services.task_service.task_crud.delete_task")
def test_delete_task_service_forbidden(mock_delete, mock_check_perms):
    mock_db = Mock()
    task_id = 42
    user_id = 42

    mock_check_perms.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_task_service(mock_db, task_id, user_id)

    mock_delete.assert_not_called()


@patch("app.services.task_service.task_crud.get_task_by_id")
@patch("app.services.task_service.task_crud.create_task_relation")
def test_create_task_relation_service_success(mock_create_relation, mock_get_task):
    mock_db = Mock()
    task_id_1 = 42
    task_id_2 = 43
    connection_id = 42
    task_1 = Mock(id=task_id_1)
    task_2 = Mock(id=task_id_2)
    connection_type = Mock(id=connection_id)
    expected_relation = Mock()

    mock_get_task.side_effect = [task_1, task_2]
    mock_db.query.return_value.filter.return_value.first.return_value = connection_type
    mock_create_relation.return_value = expected_relation

    result = create_task_relation_service(mock_db, task_id_1, task_id_2, connection_id)

    mock_create_relation.assert_called_once_with(
        mock_db, task_id_1, task_id_2, connection_id
    )
    assert result is expected_relation


@patch("app.services.task_service.task_crud.get_task_by_id")
@patch("app.services.task_service.task_crud.create_task_relation")
def test_create_task_relation_service_task_not_found(
    mock_create_relation, mock_get_task
):
    mock_db = Mock()
    task_id_1 = 42
    task_id_2 = 43
    connection_id = 42

    mock_get_task.side_effect = [Mock(), None]

    with pytest.raises(exception.NotFoundError):
        create_task_relation_service(mock_db, task_id_1, task_id_2, connection_id)

    mock_create_relation.assert_not_called()


@patch("app.services.task_service.task_crud.get_task_by_id")
@patch("app.services.task_service.task_crud.create_task_relation")
def test_create_task_relation_service_same_task(mock_create_relation, mock_get_task):
    mock_db = Mock()
    task_id = 42
    connection_id = 42

    mock_get_task.side_effect = [Mock(), Mock()]

    with pytest.raises(exception.ConflictError):
        create_task_relation_service(mock_db, task_id, task_id, connection_id)

    mock_create_relation.assert_not_called()


@patch("app.services.task_service.task_crud.get_task_by_id")
@patch("app.services.task_service.task_crud.create_task_relation")
def test_create_task_relation_service_connection_type_not_found(
    mock_create_relation, mock_get_task
):
    mock_db = Mock()
    task_id_1 = 42
    task_id_2 = 43
    connection_id = 42

    mock_get_task.side_effect = [Mock(), Mock()]
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        create_task_relation_service(mock_db, task_id_1, task_id_2, connection_id)

    mock_create_relation.assert_not_called()
