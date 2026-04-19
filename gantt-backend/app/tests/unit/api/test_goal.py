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
def test_create_goal_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        "/api/stream/42/goal/new", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_success(mock_service, mock_user, current_user, goal, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = goal

    response = client.patch(
        "/api/goal/42", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test goal"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        "/api/goal/42", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        "/api/goal/42", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_conflict(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    response = client.patch(
        "/api/goal/42", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 409


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.delete_goal_service")
def test_delete_goal_success(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete("/api/goal/42", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.delete_goal_service")
def test_delete_goal_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete("/api/goal/42", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.delete_goal_service")
def test_delete_goal_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete("/api/goal/42", headers=auth_headers)

    assert response.status_code == 403
