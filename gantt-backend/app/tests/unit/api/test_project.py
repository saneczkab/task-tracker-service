from unittest.mock import patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.update_project_service")
def test_update_project_success(
    mock_service, mock_user, current_user, project, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = project

    response = client.patch(
        f"/api/project/{project.id}", json={"name": "Test proj"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project.id
    assert data["name"] == project.name
    assert data["team_id"] == project.team_id


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.update_project_service")
def test_update_project_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        f"/api/project/{current_user.id}", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.update_project_service")
def test_update_project_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        f"/api/project/{current_user.id}", json={"name": "Test"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.delete_project_service")
def test_delete_project_success(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete(f"/api/project/{current_user.id}", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.delete_project_service")
def test_delete_project_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(f"/api/project/{current_user.id}", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.delete_project_service")
def test_delete_project_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(f"/api/project/{current_user.id}", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_project_tasks_service")
def test_get_project_tasks_success(
    mock_service, mock_user, current_user, project, task, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [task]

    response = client.get(f"/api/project/{project.id}/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == task.id
    assert data[0]["name"] == task.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_project_tasks_service")
def test_get_project_tasks_not_found(
    mock_service, mock_user, current_user, project, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/project/{project.id}/tasks", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.get_project_tasks_service")
def test_get_project_tasks_forbidden(
    mock_service, mock_user, current_user, project, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/project/{project.id}/tasks", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_project_streams_service")
def test_get_project_streams_success(
    mock_service, mock_user, current_user, stream, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [stream]

    response = client.get(
        f"/api/project/{stream.project_id}/streams", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == stream.id
    assert data[0]["name"] == stream.name
    assert data[0]["project_id"] == stream.project_id


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_project_streams_service")
def test_get_project_streams_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(
        f"/api/project/{current_user.id}/streams", headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.get_project_streams_service")
def test_get_project_streams_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(
        f"/api/project/{current_user.id}/streams", headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_success(
    mock_service, mock_user, current_user, stream, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = stream

    response = client.post(
        f"/api/project/{stream.project_id}/stream/new",
        json={"name": "Test stream"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == stream.id
    assert data["name"] == "Test stream"
    assert data["project_id"] == stream.project_id


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        f"/api/project/{current_user.id}/stream/new",
        json={"name": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_conflict(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    response = client.post(
        f"/api/project/{current_user.id}/stream/new",
        json={"name": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 409


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.stream_service.create_stream_service")
def test_create_stream_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        f"/api/project/{current_user.id}/stream/new",
        json={"name": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 403
