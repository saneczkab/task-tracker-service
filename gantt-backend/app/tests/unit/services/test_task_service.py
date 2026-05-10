from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.models import meta as meta_model
from app.models import project as project_model
from app.models import stream as stream_model
from app.models import tag as tag_model
from app.models import task as task_model
from app.models import team as team_model
from app.models import user as user_model
from app.services.task_service import (
    create_task_relation_service,
    create_task_service,
    delete_task_service,
    delete_task_custom_field_service,
    delete_task_relation_service,
    get_all_tasks_service,
    get_task_history_service,
    get_project_tasks_service,
    get_stream_tasks_service,
    update_task_service,
)


@patch("app.services.task_service.task_crud.get_tasks_by_project")
def test_get_project_tasks_service_success(
    mock_get_tasks_by_project, mock_db, ids, make_query_router, make_query
):
    project_obj = Mock()
    project_obj.team.id = ids.team_id
    user_team = Mock()
    expected_tasks = [Mock(), Mock()]

    q_project = make_query(first=project_obj)
    q_user_team = make_query(first=user_team)

    mock_db.query.side_effect = make_query_router(
        {project_model.Project: q_project, team_model.UserTeam: q_user_team}
    )
    mock_get_tasks_by_project.return_value = expected_tasks

    result = get_project_tasks_service(mock_db, ids.project_id, ids.user_id)

    mock_get_tasks_by_project.assert_called_once_with(mock_db, project_obj)
    assert result is expected_tasks


def test_get_project_tasks_service_forbidden(
    mock_db, ids, make_query_router, make_query
):
    project_obj = Mock()
    project_obj.team.id = ids.team_id

    q_project = make_query(first=project_obj)
    q_user_team = make_query(first=None)

    mock_db.query.side_effect = make_query_router(
        {project_model.Project: q_project, team_model.UserTeam: q_user_team}
    )

    with pytest.raises(exception.ForbiddenError):
        get_project_tasks_service(mock_db, ids.project_id, ids.user_id)


@patch("app.services.task_service.task_crud.get_tasks_by_stream")
@patch("app.services.task_service.permissions.check_stream_access")
def test_get_stream_tasks_service_success(
    mock_check_stream_access, mock_get_tasks_by_stream, mock_db, ids
):
    expected_tasks = [Mock()]
    mock_get_tasks_by_stream.return_value = expected_tasks

    result = get_stream_tasks_service(mock_db, ids.stream_id, ids.user_id)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id
    )
    mock_get_tasks_by_stream.assert_called_once_with(mock_db, ids.stream_id)
    assert result is expected_tasks


@patch("app.services.task_service.task_crud.create_task")
@patch("app.services.task_service.permissions.check_stream_access")
def test_create_task_service_success_with_assignee(
    mock_check_stream_access,
    mock_create_task,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
    mock_second_user,
):
    task_data = Mock(
        position=1, assignee_email="assignee@test.com", tag_ids=None, custom_fields=None
    )
    new_task = mock_task
    assignee_user = mock_second_user

    mock_create_task.return_value = new_task

    q_user = make_query(first=assignee_user)
    mock_db.query.side_effect = make_query_router({user_model.User: q_user})

    result = create_task_service(mock_db, ids.stream_id, ids.user_id, task_data)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id, need_lead=True
    )
    mock_create_task.assert_called_once_with(mock_db, ids.stream_id, task_data)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(new_task)
    assert result is new_task


@patch("app.services.task_service.task_crud.create_task")
@patch("app.services.task_service.permissions.check_stream_access")
def test_create_task_service_assignee_not_found(
    _mock_check_stream_access,
    mock_create_task,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
):
    task_data = Mock(
        position=1, assignee_email="missing@test.com", tag_ids=None, custom_fields=None
    )
    mock_create_task.return_value = mock_task

    q_user = make_query(first=None)
    mock_db.query.side_effect = make_query_router({user_model.User: q_user})

    with pytest.raises(exception.NotFoundError):
        create_task_service(mock_db, ids.stream_id, ids.user_id, task_data)


@patch.multiple(
    "app.services.task_service.task_crud",
    create_task_history_entries=DEFAULT,
    update_task=DEFAULT,
)
@patch("app.services.task_service.permissions.check_task_access")
def test_update_task_service_success_without_changes(
    mock_check_task_access,
    mock_db,
    ids,
    **mocks,
):
    task_obj = Mock(id=ids.task_id, assigned_users=[], tags=[], custom_field_values=[])
    stream_obj = Mock()
    project_obj = Mock()
    team_obj = Mock()
    task_update_data = Mock(
        assignee_email=None,
        tag_ids=None,
        custom_fields=None,
        model_fields_set=set(),
    )
    task_update_data.model_dump.return_value = {}
    mock_check_task_access.return_value = (task_obj, stream_obj, project_obj, team_obj)

    result = update_task_service(mock_db, ids.task_id, ids.user_id, task_update_data)

    mock_check_task_access.assert_called_once_with(
        mock_db, ids.task_id, ids.user_id, need_lead=True
    )
    mocks["update_task"].assert_called_once_with(mock_db, task_obj, {})
    mocks["create_task_history_entries"].assert_not_called()
    assert result is task_obj


@patch("app.services.task_service.task_crud.delete_task")
@patch("app.services.task_service.permissions.check_task_access")
def test_delete_task_service_success(
    mock_check_task_access,
    mock_delete_task,
    mock_db,
    ids,
    make_query_router,
    make_query,
):
    task_obj = Mock(id=ids.task_id)
    old_user_task = Mock()
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), Mock())

    q_user_task = make_query(first=old_user_task)
    mock_db.query.side_effect = make_query_router({meta_model.UserTask: q_user_task})

    delete_task_service(mock_db, ids.task_id, ids.user_id)

    mock_check_task_access.assert_called_once_with(
        mock_db, ids.task_id, ids.user_id, need_lead=True
    )
    mock_db.delete.assert_called_once_with(old_user_task)
    mock_delete_task.assert_called_once_with(mock_db, task_obj)


@patch.multiple(
    "app.services.task_service.task_crud",
    create_task_relation=DEFAULT,
    get_task_by_id=DEFAULT,
)
def test_create_task_relation_service_success(
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
    mock_second_user,
    mock_connection_type,
    **mocks,
):
    task_1 = mock_task
    task_2 = mock_second_user
    connection_type = mock_connection_type
    expected_relation = Mock()

    mocks["get_task_by_id"].side_effect = [task_1, task_2]

    q_connection = make_query(first=connection_type)
    mock_db.query.side_effect = make_query_router(
        {meta_model.ConnectionType: q_connection}
    )
    mocks["create_task_relation"].return_value = expected_relation

    result = create_task_relation_service(
        mock_db, task_1.id, task_2.id, connection_type.id
    )

    assert mocks["get_task_by_id"].call_count == 2
    mocks["create_task_relation"].assert_called_once_with(
        mock_db,
        task_1.id,
        task_2.id,
        connection_type.id,
    )
    assert result is expected_relation


@patch.multiple(
    "app.services.task_service.task_crud",
    create_task_relation=DEFAULT,
    get_task_by_id=DEFAULT,
)
def test_create_task_relation_service_same_task_conflict(mock_db, ids, **mocks):
    task_obj = Mock(id=ids.task_id)
    mocks["get_task_by_id"].side_effect = [task_obj, task_obj]

    with pytest.raises(exception.ConflictError):
        create_task_relation_service(
            mock_db, task_obj.id, task_obj.id, ids.connection_id
        )

    mocks["create_task_relation"].assert_not_called()


def test_get_all_tasks_service_empty_user_teams(
    mock_db, ids, make_query_router, make_query
):
    q_user_team = make_query(all_=[])
    mock_db.query.side_effect = make_query_router({team_model.UserTeam: q_user_team})

    result = get_all_tasks_service(mock_db, ids.user_id)

    assert result == []


def test_get_all_tasks_service_enriches_tasks(
    mock_db, ids, make_query_router, make_query
):
    user_team = Mock(team_id=ids.team_id)
    project_obj = Mock(team_id=ids.team_id)
    project_obj.name = "Project A"
    project_obj.team = Mock()
    project_obj.team.name = "Team A"
    stream_obj = Mock(id=ids.stream_id)
    stream_obj.name = "Stream A"
    task_obj = Mock(
        id=ids.task_id, assigned_users=[Mock(user=Mock(email="assignee@test.com"))]
    )

    q_user_team = make_query(all_=[user_team])
    q_projects = make_query(all_=[project_obj])
    q_tasks = make_query(all_=[task_obj])

    project_obj.streams = [stream_obj]
    mock_db.query.side_effect = make_query_router(
        {
            team_model.UserTeam: q_user_team,
            project_model.Project: q_projects,
            task_model.Task: q_tasks,
        }
    )

    result = get_all_tasks_service(mock_db, ids.user_id)

    assert result == [task_obj]
    assert task_obj.team_id == ids.team_id
    assert task_obj.team_name == "Team A"
    assert task_obj.project_name == "Project A"
    assert task_obj.stream_name == "Stream A"
    assert task_obj.assignee_email == "assignee@test.com"


def test_get_project_tasks_service_not_found(
    mock_db, ids, make_query_router, make_query
):
    q_project = make_query(first=None)
    mock_db.query.side_effect = make_query_router({project_model.Project: q_project})

    with pytest.raises(exception.NotFoundError, match="Проект не найден"):
        get_project_tasks_service(mock_db, ids.project_id, ids.user_id)


@patch("app.services.task_service.custom_field_crud.set_task_custom_field_value")
@patch("app.services.task_service.task_crud.create_task")
@patch("app.services.task_service.permissions.check_stream_access")
def test_create_task_service_auto_position_and_custom_fields(
    mock_check_stream_access,
    mock_create_task,
    mock_set_custom_field_value,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
):
    task_data = Mock(
        position=None,
        assignee_email=None,
        tag_ids=None,
        custom_fields=[Mock(custom_field_id=1, value="8")],
    )
    last_pos = Mock(position=2)
    new_task = mock_task

    q_last_pos = make_query(order_by_first=last_pos)
    mock_db.query.side_effect = make_query_router({task_model.Task: q_last_pos})
    mock_create_task.return_value = new_task

    result = create_task_service(mock_db, ids.stream_id, ids.user_id, task_data)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id, need_lead=True
    )
    assert task_data.position == 3
    mock_create_task.assert_called_once_with(mock_db, ids.stream_id, task_data)
    mock_set_custom_field_value.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(new_task)
    assert result is new_task


@patch("app.services.task_service.task_crud.create_task")
@patch("app.services.task_service.permissions.check_stream_access")
def test_create_task_service_stream_not_found(
    mock_check_stream_access,
    mock_create_task,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
):
    task_data = Mock(position=1, assignee_email=None, tag_ids=[1], custom_fields=None)

    q_stream = make_query(first=None)
    mock_db.query.side_effect = make_query_router({stream_model.Stream: q_stream})
    mock_create_task.return_value = mock_task

    with pytest.raises(exception.NotFoundError, match="Стрим не найден"):
        create_task_service(mock_db, ids.stream_id, ids.user_id, task_data)

    mock_check_stream_access.assert_called_once_with(
        mock_db, ids.stream_id, ids.user_id, need_lead=True
    )


@patch("app.services.task_service.task_crud.create_task")
@patch("app.services.task_service.permissions.check_stream_access")
def test_create_task_service_tag_not_found(
    mock_check_stream_access,
    mock_create_task,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
):
    task_data = Mock(
        position=1, assignee_email=None, tag_ids=[ids.connection_id], custom_fields=None
    )
    new_task = mock_task
    stream_obj = Mock()
    stream_obj.project = Mock(team_id=ids.team_id)

    q_stream = make_query(first=stream_obj)
    q_tag = make_query(first=None)

    mock_db.query.side_effect = make_query_router(
        {stream_model.Stream: q_stream, tag_model.Tag: q_tag}
    )
    mock_create_task.return_value = new_task

    with pytest.raises(
        exception.NotFoundError, match=f"Тег с id {ids.connection_id} не найден"
    ):
        create_task_service(mock_db, ids.stream_id, ids.user_id, task_data)


@patch("app.services.task_service.task_crud.create_task")
@patch("app.services.task_service.permissions.check_stream_access")
def test_create_task_service_tag_forbidden(
    mock_check_stream_access,
    mock_create_task,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_task,
):
    task_data = Mock(
        position=1, assignee_email=None, tag_ids=[ids.connection_id], custom_fields=None
    )
    new_task = mock_task
    stream_obj = Mock()
    stream_obj.project = Mock(team_id=ids.team_id)
    tag_obj = Mock(team_id=ids.team_id + 1)

    q_stream = make_query(first=stream_obj)
    q_tag = make_query(first=tag_obj)

    mock_db.query.side_effect = make_query_router(
        {stream_model.Stream: q_stream, tag_model.Tag: q_tag}
    )
    mock_create_task.return_value = new_task

    with pytest.raises(
        exception.ForbiddenError, match="Тег принадлежит другой команде"
    ):
        create_task_service(mock_db, ids.stream_id, ids.user_id, task_data)


@patch.multiple(
    "app.services.task_service.custom_field_crud",
    set_task_custom_field_value=DEFAULT,
)
@patch.multiple(
    "app.services.task_service.task_crud",
    create_task_history_entries=DEFAULT,
    update_task=DEFAULT,
)
@patch("app.services.task_service.permissions.check_task_access")
def test_update_task_service_success_with_changes(
    mock_check_task_access,
    mock_db,
    ids,
    make_query_router,
    make_query,
    mock_second_user,
    mock_team,
    **mocks,
):
    task_obj = Mock(
        id=ids.task_id,
        name="Old task",
        description="Old description",
        status_id=1,
        priority_id=1,
        start_date=None,
        deadline=None,
        position=1,
        assigned_users=[Mock(user=Mock(email="old@test.com"))],
        tags=[Mock(tag_id=1)],
        custom_field_values=[Mock(custom_field_id=10, value="old")],
    )
    stream_obj = Mock()
    project_obj = Mock()
    team_obj = mock_team
    assignee_user = mock_second_user
    old_user_task = Mock()
    tag_obj = Mock(team_id=ids.team_id)
    task_update_data = Mock(
        name="New task",
        description="Old description",
        status_id=1,
        priority_id=1,
        start_date=None,
        deadline=None,
        position=1,
        assignee_email="new@test.com",
        tag_ids=[2],
        custom_fields=[Mock(custom_field_id=10, value="new")],
        model_fields_set={"name", "assignee_email", "tag_ids", "custom_fields"},
    )
    task_update_data.model_dump.return_value = {
        "name": "New task",
        "assignee_email": "new@test.com",
        "tag_ids": [2],
    }

    q_user = make_query(first=assignee_user)
    q_old_user_task = make_query(first=old_user_task)
    q_tag_delete = make_query()
    q_tag_lookup = make_query(first=tag_obj)

    mock_db.query.side_effect = make_query_router(
        {
            user_model.User: q_user,
            meta_model.UserTask: q_old_user_task,
            tag_model.TaskTag: q_tag_delete,
            tag_model.Tag: q_tag_lookup,
        }
    )
    mock_check_task_access.return_value = (task_obj, stream_obj, project_obj, team_obj)

    result = update_task_service(mock_db, ids.task_id, ids.user_id, task_update_data)

    mock_check_task_access.assert_called_once_with(
        mock_db, ids.task_id, ids.user_id, need_lead=True
    )
    mocks["update_task"].assert_called_once_with(
        mock_db,
        task_obj,
        {"name": "New task", "assignee_email": "new@test.com", "tag_ids": [2]},
    )
    mocks["create_task_history_entries"].assert_called_once()
    assert set(mocks["create_task_history_entries"].call_args.args[3]) == {
        "name",
        "assignee_email",
        "tag_ids",
        "custom_fields",
    }
    mocks["set_task_custom_field_value"].assert_called_once()
    mock_db.delete.assert_called_once_with(old_user_task)
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()
    assert result is task_obj


@patch("app.services.task_service.permissions.check_task_access")
def test_update_task_service_assignee_not_found(
    mock_check_task_access, mock_db, ids, make_query_router, make_query
):
    task_obj = Mock(assigned_users=[], tags=[], custom_field_values=[])
    task_update_data = Mock(
        assignee_email="missing@test.com",
        tag_ids=None,
        custom_fields=None,
        model_fields_set={"assignee_email"},
    )
    task_update_data.model_dump.return_value = {"assignee_email": "missing@test.com"}

    q_user = make_query(first=None)
    mock_db.query.side_effect = make_query_router({user_model.User: q_user})
    mock_check_task_access.return_value = (
        task_obj,
        Mock(),
        Mock(),
        Mock(id=ids.team_id),
    )

    with pytest.raises(exception.NotFoundError, match="Пользователь не найден"):
        update_task_service(mock_db, ids.task_id, ids.user_id, task_update_data)


@patch("app.services.task_service.permissions.check_task_access")
def test_update_task_service_tag_not_found(
    mock_check_task_access, mock_db, ids, make_query_router, make_query
):
    task_obj = Mock(
        name="Old",
        description=None,
        status_id=None,
        priority_id=None,
        start_date=None,
        deadline=None,
        position=1,
        assigned_users=[],
        tags=[Mock(tag_id=1)],
        custom_field_values=[],
    )
    team_obj = Mock(id=ids.team_id)
    task_update_data = Mock(
        assignee_email=None,
        tag_ids=[2],
        custom_fields=None,
        model_fields_set={"tag_ids"},
    )
    task_update_data.model_dump.return_value = {"tag_ids": [2]}

    q_tag_delete = make_query()
    q_tag_lookup = make_query(first=None)

    mock_db.query.side_effect = make_query_router(
        {tag_model.TaskTag: q_tag_delete, tag_model.Tag: q_tag_lookup}
    )
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), team_obj)

    with pytest.raises(exception.NotFoundError, match="Тег с id 2 не найден"):
        update_task_service(mock_db, ids.task_id, ids.user_id, task_update_data)


@patch("app.services.task_service.permissions.check_task_access")
def test_update_task_service_tag_forbidden(
    mock_check_task_access, mock_db, ids, make_query_router, make_query
):
    task_obj = Mock(
        name="Old",
        description=None,
        status_id=None,
        priority_id=None,
        start_date=None,
        deadline=None,
        position=1,
        assigned_users=[],
        tags=[Mock(tag_id=1)],
        custom_field_values=[],
    )
    team_obj = Mock(id=ids.team_id)
    tag_obj = Mock(team_id=ids.team_id + 1)
    task_update_data = Mock(
        assignee_email=None,
        tag_ids=[2],
        custom_fields=None,
        model_fields_set={"tag_ids"},
    )
    task_update_data.model_dump.return_value = {"tag_ids": [2]}

    q_tag_delete = make_query()
    q_tag_lookup = make_query(first=tag_obj)

    mock_db.query.side_effect = make_query_router(
        {tag_model.TaskTag: q_tag_delete, tag_model.Tag: q_tag_lookup}
    )
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), team_obj)

    with pytest.raises(
        exception.ForbiddenError, match="Тег принадлежит другой команде"
    ):
        update_task_service(mock_db, ids.task_id, ids.user_id, task_update_data)


@patch("app.services.task_service.permissions.check_task_access")
def test_delete_task_relation_service_success(
    mock_check_task_access, mock_db, ids, make_query_router, make_query, mock_task
):
    relation = Mock(id=ids.connection_id, task_id_1=mock_task.id)

    q_relation = make_query(first=relation)
    mock_db.query.side_effect = make_query_router({task_model.TaskRelation: q_relation})
    mock_check_task_access.return_value = (Mock(), Mock(), Mock(), Mock())

    delete_task_relation_service(mock_db, relation.id, ids.user_id)

    mock_check_task_access.assert_called_once_with(
        mock_db, relation.task_id_1, ids.user_id, need_lead=True
    )
    mock_db.delete.assert_called_once_with(relation)
    mock_db.commit.assert_called_once()


def test_delete_task_relation_service_not_found(
    mock_db, ids, make_query_router, make_query
):
    q_relation = make_query(first=None)
    mock_db.query.side_effect = make_query_router({task_model.TaskRelation: q_relation})

    with pytest.raises(exception.NotFoundError, match="Связь не найдена"):
        delete_task_relation_service(mock_db, ids.connection_id, ids.user_id)


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_create_task_relation_service_task_not_found(mock_get_task_by_id, mock_db, ids):
    mock_get_task_by_id.side_effect = [None, Mock(id=ids.second_user_id)]

    with pytest.raises(exception.NotFoundError, match="Одна из задач не найдена"):
        create_task_relation_service(
            mock_db, ids.task_id, ids.second_user_id, ids.connection_id
        )


@patch("app.services.task_service.task_crud.get_task_by_id")
def test_create_task_relation_service_connection_not_found(
    mock_get_task_by_id, mock_db, ids, make_query
):
    task_1 = Mock(id=ids.task_id)
    task_2 = Mock(id=ids.second_user_id)
    mock_db.query.return_value = make_query(first=None)
    mock_get_task_by_id.side_effect = [task_1, task_2]

    with pytest.raises(exception.NotFoundError, match="Тип связи не найден"):
        create_task_relation_service(mock_db, task_1.id, task_2.id, ids.connection_id)


@patch("app.services.task_service.task_crud.get_task_history")
@patch("app.services.task_service.permissions.check_task_access")
def test_get_task_history_service_success(
    mock_check_task_access, mock_get_task_history, mock_db, ids
):
    task_obj = Mock(id=ids.task_id)
    history_entry = Mock(
        id=1, task_id=ids.task_id, changed_by=Mock(email="changer@test.com")
    )
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), Mock())
    mock_get_task_history.return_value = [history_entry]

    result = get_task_history_service(mock_db, ids.task_id, ids.user_id)

    mock_check_task_access.assert_called_once_with(mock_db, ids.task_id, ids.user_id)
    mock_get_task_history.assert_called_once_with(mock_db, ids.task_id)
    assert result is mock_get_task_history.return_value
    assert history_entry.changed_by_email == "changer@test.com"


@patch("app.services.task_service.custom_field_crud.delete_task_custom_field_value")
@patch("app.services.task_service.permissions.check_task_access")
def test_delete_task_custom_field_service_success(
    mock_check_task_access, mock_delete_value, mock_db, ids, make_query
):
    task_obj = Mock(id=ids.task_id)
    team_obj = Mock()
    custom_field_obj = Mock(id=1)
    mock_db.query.return_value = make_query(first=custom_field_obj)
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), team_obj)
    expected = Mock()
    mock_delete_value.return_value = expected

    result = delete_task_custom_field_service(
        mock_db, ids.task_id, custom_field_obj.id, ids.user_id
    )

    mock_delete_value.assert_called_once_with(mock_db, ids.task_id, custom_field_obj.id)
    assert result is expected


@patch("app.services.task_service.permissions.check_task_access")
def test_delete_task_custom_field_service_not_found(
    mock_check_task_access, mock_db, ids, make_query
):
    task_obj = Mock(id=ids.task_id)
    team_obj = Mock()
    mock_db.query.return_value = make_query(first=None)
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), team_obj)

    with pytest.raises(exception.NotFoundError):
        delete_task_custom_field_service(mock_db, ids.task_id, 1, ids.user_id)
