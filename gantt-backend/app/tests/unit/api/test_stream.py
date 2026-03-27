from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.core import exception
from main import app

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def current_user():
    user = Mock()
    user.id = 42
    return user


@pytest.fixture
def stream():
    obj = Mock()
    obj.id = 42
    obj.name = "Test stream"
    obj.project_id = 42
    return obj


@pytest.fixture
def task():
    obj = Mock()
    obj.id = 42
    obj.name = "Test task"
    obj.description = None
    obj.status_id = None
    obj.priority_id = None
    obj.stream_id = 42
    obj.start_date = None
    obj.deadline = None
    obj.assignee_email = None
    obj.position = 1
    obj.relations = []
    return obj


@pytest.fixture
def goal():
    obj = Mock()
    obj.id = 42
    obj.name = "Test goal"
    obj.description = None
    obj.start_date = None
    obj.deadline = None
    obj.stream_id = 42
    obj.position = 1
    return obj


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
@patch("app.services.goal_service.get_stream_goals_service")
def test_get_stream_goals_success(
    mock_service, mock_user, current_user, goal, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = [goal]

    response = client.get("/api/stream/42/goals", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["name"] == "Test goal"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.get_stream_goals_service")
def test_get_stream_goals_not_found(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/stream/42/goals", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.get_stream_goals_service")
def test_get_stream_goals_forbidden(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/stream/42/goals", headers=auth_headers)

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
def test_create_goal_success(mock_service, mock_user, current_user, goal, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = goal

    response = client.post(
        "/api/stream/42/goal/new", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test goal"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.create_goal_service")
def test_create_goal_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/stream/42/goal/new", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 404


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
