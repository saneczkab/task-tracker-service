from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core import exception
from main import app

client = TestClient(app, raise_server_exceptions=False)


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.user_service.get_user_by_token_service")
def test_get_user_by_token_success(
    mock_service, mock_user, current_user, team, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = (current_user, [team])

    response = client.get("/api/user_by_token", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "test_user"
    assert len(data["teams"]) == 1
    assert data["teams"][0]["id"] == 42
    assert data["teams"][0]["name"] == "Test team"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.user_service.get_user_by_token_service")
def test_get_user_by_token_not_found(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/user_by_token", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.user_service.get_user_service")
def test_get_user_success(mock_service, mock_user, current_user, team, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = (current_user, [team])

    response = client.get("/api/user/42", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "test_user"
    assert len(data["teams"]) == 1
    assert data["teams"][0]["id"] == 42
    assert data["teams"][0]["name"] == "Test team"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.user_service.get_user_service")
def test_get_user_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/user/42", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.user_service.get_user_service")
def test_get_user_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/user/42", headers=auth_headers)

    assert response.status_code == 404
