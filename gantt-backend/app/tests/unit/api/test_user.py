from unittest.mock import DEFAULT, patch

from app.core import exception


class ValidationError(Exception):
    pass


@patch.multiple(
    "app.services.user_service",
    get_current_user_service=DEFAULT,
    get_user_by_token_service=DEFAULT,
)
def test_get_user_by_token_success(client, current_user, team, auth_headers, **mocks):
    mocks["get_current_user_service"].return_value = current_user
    mocks["get_user_by_token_service"].return_value = (current_user, [team])

    response = client.get("/api/user_by_token", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == current_user.id
    assert data["email"] == current_user.email
    assert data["nickname"] == current_user.nickname
    assert len(data["teams"]) == 1
    assert data["teams"][0]["id"] == team.id
    assert data["teams"][0]["name"] == team.name


@patch.multiple(
    "app.services.user_service",
    get_current_user_service=DEFAULT,
    get_user_by_token_service=DEFAULT,
)
def test_get_user_by_token_not_found(client, current_user, auth_headers, **mocks):
    mocks["get_current_user_service"].return_value = current_user
    mocks["get_user_by_token_service"].side_effect = exception.NotFoundError()

    response = client.get("/api/user_by_token", headers=auth_headers)

    assert response.status_code == 404


@patch.multiple(
    "app.services.user_service",
    get_current_user_service=DEFAULT,
    get_user_service=DEFAULT,
)
def test_get_user_success(client, current_user, team, auth_headers, **mocks):
    mocks["get_current_user_service"].return_value = current_user
    mocks["get_user_service"].return_value = (current_user, [team])

    response = client.get(f"/api/user/{current_user.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == current_user.id
    assert data["email"] == current_user.email
    assert data["nickname"] == current_user.nickname
    assert len(data["teams"]) == 1
    assert data["teams"][0]["id"] == team.id
    assert data["teams"][0]["name"] == team.name


@patch.multiple(
    "app.services.user_service",
    get_current_user_service=DEFAULT,
    get_user_service=DEFAULT,
)
def test_get_user_forbidden(client, current_user, auth_headers, **mocks):
    mocks["get_current_user_service"].return_value = current_user
    mocks["get_user_service"].side_effect = exception.ForbiddenError()

    response = client.get(f"/api/user/{current_user.id}", headers=auth_headers)

    assert response.status_code == 403


@patch.multiple(
    "app.services.user_service",
    get_current_user_service=DEFAULT,
    get_user_service=DEFAULT,
)
def test_get_user_not_found(client, current_user, auth_headers, **mocks):
    mocks["get_current_user_service"].return_value = current_user
    mocks["get_user_service"].side_effect = exception.NotFoundError()

    response = client.get(f"/api/user/{current_user.id}", headers=auth_headers)

    assert response.status_code == 404
