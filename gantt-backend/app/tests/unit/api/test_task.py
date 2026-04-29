from datetime import datetime
from unittest.mock import Mock, patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.update_task_service")
def test_update_task_success(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = task

    response = client.patch(
        f"/api/task/{task.id}", json={"name": "Test task"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["name"] == task.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.update_task_service")
def test_update_task_not_found(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        f"/api/task/{task.id}", json={"name": "Test task"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.update_task_service")
def test_update_task_forbidden(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        f"/api/task/{task.id}", json={"name": "Test task"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_service")
def test_delete_task_success(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete(f"/api/task/{task.id}", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_service")
def test_delete_task_not_found(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(f"/api/task/{task.id}", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_service")
def test_delete_task_forbidden(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(f"/api/task/{task.id}", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.task_service.create_task_relation_service")
def test_create_task_relation_success(mock_service, relation, auth_headers, client):
    mock_service.return_value = relation

    response = client.post(
        f"/api/task/{relation.task_id_1}/relation",
        json={"task_id": relation.task_id_2, "connection_id": relation.connection_id},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == relation.id
    assert data["task_id_1"] == relation.task_id_1
    assert data["task_id_2"] == relation.task_id_2
    assert data["connection_id"] == relation.connection_id
    assert data["connection_name"] == relation.connection.name


@patch("app.services.task_service.create_task_relation_service")
def test_create_task_relation_not_found(mock_service, relation, auth_headers, client):
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        f"/api/task/{relation.task_id_1}/relation",
        json={"task_id": relation.task_id_2, "connection_id": relation.connection_id},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.task_service.create_task_relation_service")
def test_create_task_relation_conflict(mock_service, relation, auth_headers, client):
    mock_service.side_effect = exception.ConflictError()

    response = client.post(
        f"/api/task/{relation.task_id_1}/relation",
        json={"task_id": relation.task_id_2, "connection_id": relation.connection_id},
        headers=auth_headers,
    )

    assert response.status_code == 400


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_all_tasks_service")
def test_get_all_tasks_success(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [task]

    response = client.get("/api/tasks/all", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == task.id
    assert data[0]["name"] == task.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_task_history_service")
def test_get_task_history_not_found(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/task/{task.id}/history", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_task_history_service")
def test_get_task_history_forbidden(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/task/{task.id}/history", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_custom_field_service")
def test_delete_task_custom_field_not_found(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(
        f"/api/task/{task.id}/custom_fields/1",
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_custom_field_service")
def test_delete_task_custom_field_forbidden(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(
        f"/api/task/{task.id}/custom_fields/1",
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_task_history_service")
def test_get_task_history_success(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user
    history_entry = Mock(
        id=1,
        task_id=task.id,
        changed_by_id=current_user.id,
        changed_by_email=current_user.email,
        changed_at=datetime(2026, 1, 1, 12, 0, 0),
        field_name="name",
        old_value="Old task",
        new_value="New task",
    )
    history_entry.changed_by = Mock(email=current_user.email)
    mock_service.return_value = [history_entry]

    response = client.get(f"/api/task/{task.id}/history", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == history_entry.id
    assert data[0]["task_id"] == history_entry.task_id
    assert data[0]["changed_by_email"] == history_entry.changed_by_email
    assert data[0]["field_name"] == history_entry.field_name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_custom_field_service")
def test_delete_task_custom_field_success(
    mock_service, mock_user, current_user, task, auth_headers, client
):
    mock_user.return_value = current_user

    response = client.delete(
        f"/api/task/{task.id}/custom_fields/1",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert mock_service.call_args.args[1:] == (task.id, 1, current_user.id)
