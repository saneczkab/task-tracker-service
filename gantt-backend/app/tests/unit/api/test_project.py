from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core import exception
from main import app

client = TestClient(app, raise_server_exceptions=False)


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.update_project_service")
def test_update_project_success(
    mock_service, mock_user, current_user, project, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = project

    response = client.patch(
        "/api/project/42", json={"name": "Test proj"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == project.name
    assert data["team_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.update_project_service")
def test_update_project_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        "/api/project/42", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.update_project_service")
def test_update_project_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        "/api/project/42", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.delete_project_service")
def test_delete_project_success(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete("/api/project/42", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.delete_project_service")
def test_delete_project_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete("/api/project/42", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.delete_project_service")
def test_delete_project_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete("/api/project/42", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_project_tasks_service")
def test_get_project_tasks_success(
    mock_service, mock_user, current_user, task, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = [task]

    response = client.get("/api/project/42/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["name"] == "Test task"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_project_tasks_service")
def test_get_project_tasks_not_found(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/project/42/tasks", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_project_tasks_service")
def test_get_project_tasks_forbidden(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/project/42/tasks", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_project_streams_service")
def test_get_project_streams_success(
    mock_service, mock_user, current_user, stream, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = [stream]

    response = client.get("/api/project/42/streams", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["name"] == "Test stream"
    assert data[0]["project_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_project_streams_service")
def test_get_project_streams_not_found(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/project/42/streams", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_project_streams_service")
def test_get_project_streams_forbidden(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/project/42/streams", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_success(
    mock_service, mock_user, current_user, stream, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = stream

    response = client.post(
        "/api/project/42/stream/new", json={"name": "Test stream"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test stream"
    assert data["project_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/project/42/stream/new", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_conflict(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    response = client.post(
        "/api/project/42/stream/new", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 409


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        "/api/project/42/stream/new", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 403
