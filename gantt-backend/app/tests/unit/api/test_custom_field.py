from unittest.mock import patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.create_custom_field_service")
def test_create_custom_field_success(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = custom_field_obj

    response = client.post(
        f"/api/teams/{custom_field_obj.team_id}/custom_fields/",
        json={"name": custom_field_obj.name, "type": custom_field_obj.type.value},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == custom_field_obj.id
    assert data["team_id"] == custom_field_obj.team_id
    assert data["name"] == custom_field_obj.name
    assert data["type"] == custom_field_obj.type.value


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.create_custom_field_service")
def test_create_custom_field_forbidden(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        f"/api/teams/{custom_field_obj.team_id}/custom_fields/",
        json={"name": "Severity", "type": "string"},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.get_custom_fields_by_team_service")
def test_read_custom_fields_success(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [custom_field_obj]

    response = client.get(
        f"/api/teams/{custom_field_obj.team_id}/custom_fields/", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == custom_field_obj.id
    assert data[0]["team_id"] == custom_field_obj.team_id
    assert data[0]["name"] == custom_field_obj.name
    assert data[0]["type"] == custom_field_obj.type.value


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.get_custom_fields_by_team_service")
def test_read_custom_fields_forbidden(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(
        f"/api/teams/{custom_field_obj.team_id}/custom_fields/", headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.update_custom_field_service")
def test_update_custom_field_success(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = custom_field_obj

    response = client.put(
        f"/api/custom_fields/{custom_field_obj.id}/",
        json={"name": custom_field_obj.name, "type": custom_field_obj.type.value},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == custom_field_obj.id
    assert data["team_id"] == custom_field_obj.team_id
    assert data["name"] == custom_field_obj.name
    assert data["type"] == custom_field_obj.type.value


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.update_custom_field_service")
def test_update_custom_field_not_found(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.put(
        f"/api/custom_fields/{custom_field_obj.id}/",
        json={"name": "Severity", "type": "string"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.update_custom_field_service")
def test_update_custom_field_forbidden(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.put(
        f"/api/custom_fields/{custom_field_obj.id}/",
        json={"name": "Severity", "type": "string"},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.delete_custom_field_service")
def test_delete_custom_field_success(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = custom_field_obj

    response = client.delete(
        f"/api/custom_fields/{custom_field_obj.id}/", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == custom_field_obj.id
    assert data["team_id"] == custom_field_obj.team_id
    assert data["name"] == custom_field_obj.name
    assert data["type"] == custom_field_obj.type.value


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.delete_custom_field_service")
def test_delete_custom_field_not_found(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(
        f"/api/custom_fields/{custom_field_obj.id}/", headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.custom_field_service.delete_custom_field_service")
def test_delete_custom_field_forbidden(
    mock_service, mock_user, current_user, custom_field_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(
        f"/api/custom_fields/{custom_field_obj.id}/", headers=auth_headers
    )

    assert response.status_code == 403
