from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core import exception
from main import app

client = TestClient(app, raise_server_exceptions=False)


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_stream_service")
def test_get_stream_success(
    mock_service, mock_user, current_user, stream, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = stream

    response = client.get("/api/stream/42", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test stream"
    assert data["project_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_stream_service")
def test_get_stream_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/stream/42", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_stream_service")
def test_get_stream_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/stream/42", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.update_stream_service")
def test_update_stream_success(
    mock_service, mock_user, current_user, stream, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = stream

    response = client.patch(
        "/api/stream/42", json={"name": "Test stream"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test stream"
    assert data["project_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.update_stream_service")
def test_update_stream_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        "/api/stream/42", json={"name": "Test stream"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.update_stream_service")
def test_update_stream_conflict(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    response = client.patch(
        "/api/stream/42", json={"name": "Test stream"}, headers=auth_headers
    )

    assert response.status_code == 409


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.update_stream_service")
def test_update_stream_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        "/api/stream/42", json={"name": "Test stream"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.delete_stream_service")
def test_delete_stream_success(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete("/api/stream/42", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.delete_stream_service")
def test_delete_stream_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete("/api/stream/42", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.delete_stream_service")
def test_delete_stream_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete("/api/stream/42", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_stream_tasks_service")
def test_get_stream_tasks_success(
    mock_service, mock_user, current_user, task, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = [task]

    response = client.get("/api/stream/42/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["name"] == "Test task"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_stream_tasks_service")
def test_get_stream_tasks_not_found(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/stream/42/tasks", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_stream_tasks_service")
def test_get_stream_tasks_forbidden(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/stream/42/tasks", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.create_task_service")
def test_create_task_success(mock_service, mock_user, current_user, task, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = task

    response = client.post(
        "/api/stream/42/task/new",
        json={"name": "Test task", "status_id": None, "priority_id": None},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test task"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.create_task_service")
def test_create_task_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/stream/42/task/new",
        json={"name": "Test task", "status_id": None, "priority_id": None},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.create_task_service")
def test_create_task_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        "/api/stream/42/task/new",
        json={"name": "Test task", "status_id": None, "priority_id": None},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.create_goal_service")
def test_create_goal_conflict(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    response = client.post(
        "/api/stream/42/goal/new", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 409


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.create_goal_service")
def test_create_goal_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        "/api/stream/42/goal/new", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 403
