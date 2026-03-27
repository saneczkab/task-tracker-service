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
def relation():
    obj = Mock()
    obj.id = 42
    obj.task_id_1 = 42
    obj.task_id_2 = 43
    obj.connection_id = 42
    obj.connection_name = "Test connection"
    return obj


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.update_task_service")
def test_update_task_success(mock_service, mock_user, current_user, task, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = task

    response = client.patch(
        "/api/task/42", json={"name": "Test task"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test task"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.update_task_service")
def test_update_task_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        "/api/task/42", json={"name": "Test task"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.update_task_service")
def test_update_task_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        "/api/task/42", json={"name": "Test task"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_service")
def test_delete_task_success(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete("/api/task/42", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_service")
def test_delete_task_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete("/api/task/42", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_service")
def test_delete_task_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete("/api/task/42", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.task_service.create_task_relation_service")
def test_create_task_relation_success(mock_service, relation, auth_headers):
    mock_service.return_value = relation

    response = client.post(
        "/api/task/42/relation",
        json={"task_id": 43, "connection_id": 42},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["task_id_1"] == 42
    assert data["task_id_2"] == 43
    assert data["connection_id"] == 42
    assert data["connection_name"] == "Test connection"


@patch("app.services.task_service.create_task_relation_service")
def test_create_task_relation_not_found(mock_service, auth_headers):
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/task/42/relation",
        json={"task_id": 43, "connection_id": 42},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.task_service.create_task_relation_service")
def test_create_task_relation_conflict(mock_service, auth_headers):
    mock_service.side_effect = exception.ConflictError()

    response = client.post(
        "/api/task/42/relation",
        json={"task_id": 43, "connection_id": 42},
        headers=auth_headers,
    )

    assert response.status_code == 400
