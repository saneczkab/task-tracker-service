from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core import exception
from main import app

client = TestClient(app, raise_server_exceptions=False)


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.create_team_service")
def test_create_team_success(mock_service, mock_user, current_user, team, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = team

    response = client.post(
        "/api/team/new", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test team"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.create_team_service")
def test_create_team_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/team/new", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.update_team_service")
def test_update_team_success(mock_service, mock_user, current_user, team, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = team

    response = client.patch(
        "/api/team/42", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test team"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.update_team_service")
def test_update_team_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        "/api/team/42", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.update_team_service")
def test_update_team_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        "/api/team/42", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.delete_team_service")
def test_delete_team_success(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete("/api/team/42", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.delete_team_service")
def test_delete_team_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete("/api/team/42", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.delete_team_service")
def test_delete_team_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete("/api/team/42", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.get_team_users_service")
def test_get_team_users_success(
    mock_service, mock_user, current_user, user_with_role, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = [user_with_role]

    response = client.get("/api/team/42/users", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["nickname"] == "Test user"


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.get_team_users_service")
def test_get_team_users_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/team/42/users", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.get_team_users_service")
def test_get_team_users_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/team/42/users", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.get_team_projects_service")
def test_get_team_projects_success(
    mock_service, mock_user, current_user, project, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = [project]

    response = client.get("/api/team/42/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["name"] == project.name
    assert data[0]["team_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.get_team_projects_service")
def test_get_team_projects_not_found(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get("/api/team/42/projects", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.get_team_projects_service")
def test_get_team_projects_forbidden(
    mock_service, mock_user, current_user, auth_headers
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get("/api/team/42/projects", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.create_project_service")
def test_create_project_success(
    mock_service, mock_user, current_user, project, auth_headers
):
    mock_user.return_value = current_user
    mock_service.return_value = project

    response = client.post(
        "/api/team/42/project/new", json={"name": "Test project"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == project.name
    assert data["team_id"] == 42


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.create_project_service")
def test_create_project_not_found(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/team/42/project/new", json={"name": "Test project"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.create_project_service")
def test_create_project_forbidden(mock_service, mock_user, current_user, auth_headers):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        "/api/team/42/project/new", json={"name": "Test project"}, headers=auth_headers
    )

    assert response.status_code == 403
