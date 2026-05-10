from unittest.mock import patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.get_stream_goals_service")
def test_get_stream_goals_success(
    mock_service, mock_user, current_user, goal, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [goal]

    response = client.get(f"/api/stream/{goal.stream_id}/goals", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == goal.id
    assert data[0]["name"] == goal.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.get_stream_goals_service")
def test_get_stream_goals_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/stream/{current_user.id}/goals", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.get_stream_goals_service")
def test_get_stream_goals_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/stream/{current_user.id}/goals", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.create_goal_service")
def test_create_goal_success(
    mock_service, mock_user, current_user, goal, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = goal

    response = client.post(
        f"/api/stream/{goal.stream_id}/goal/new",
        json={"name": "Test goal"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == goal.id
    assert data["name"] == goal.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.create_goal_service")
def test_create_goal_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        f"/api/stream/{current_user.id}/goal/new",
        json={"name": "Test goal"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.create_goal_service")
def test_create_goal_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        f"/api/stream/{current_user.id}/goal/new",
        json={"name": "Test goal"},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_success(
    mock_service, mock_user, current_user, goal, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = goal

    response = client.patch(
        f"/api/goal/{goal.id}", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == goal.id
    assert data["name"] == goal.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        f"/api/goal/{current_user.id}", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        f"/api/goal/{current_user.id}", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.update_goal_service")
def test_update_goal_conflict(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    response = client.patch(
        f"/api/goal/{current_user.id}", json={"name": "Test goal"}, headers=auth_headers
    )

    assert response.status_code == 409


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.delete_goal_service")
def test_delete_goal_success(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete(f"/api/goal/{current_user.id}", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.delete_goal_service")
def test_delete_goal_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(f"/api/goal/{current_user.id}", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.goal_service.delete_goal_service")
def test_delete_goal_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(f"/api/goal/{current_user.id}", headers=auth_headers)

    assert response.status_code == 403
