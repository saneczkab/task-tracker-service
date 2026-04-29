from unittest.mock import patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.create_team_service")
def test_create_team_success(
    mock_service, mock_user, current_user, team, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = team

    response = client.post(
        "/api/team/new", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == team.id
    assert data["name"] == team.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.create_team_service")
def test_create_team_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        "/api/team/new", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.update_team_service")
def test_update_team_success(
    mock_service, mock_user, current_user, team, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = team

    response = client.patch(
        f"/api/team/{team.id}", json={"name": "Test team"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == team.id
    assert data["name"] == team.name


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.update_team_service")
def test_update_team_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.patch(
        f"/api/team/{current_user.id + 1}",
        json={"name": "Test team"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.update_team_service")
def test_update_team_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.patch(
        f"/api/team/{current_user.id + 1}",
        json={"name": "Test team"},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.delete_team_service")
def test_delete_team_success(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = None

    response = client.delete(f"/api/team/{current_user.id}", headers=auth_headers)

    assert response.status_code == 204


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.delete_team_service")
def test_delete_team_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(f"/api/team/{current_user.id + 1}", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.delete_team_service")
def test_delete_team_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(f"/api/team/{current_user.id + 1}", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.get_team_users_service")
def test_get_team_users_success(
    mock_service, mock_user, current_user, user_with_role, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [user_with_role]

    response = client.get(f"/api/team/{user_with_role.id}/users", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == user_with_role.id
    assert data[0]["nickname"] == user_with_role.nickname


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.get_team_users_service")
def test_get_team_users_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/team/{current_user.id}/users", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.team_service.get_team_users_service")
def test_get_team_users_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/team/{current_user.id}/users", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.get_team_projects_service")
def test_get_team_projects_success(
    mock_service, mock_user, current_user, project, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [project]

    response = client.get(f"/api/team/{project.team_id}/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == project.id
    assert data[0]["name"] == project.name
    assert data[0]["team_id"] == project.team_id


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.get_team_projects_service")
def test_get_team_projects_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/team/{current_user.id}/projects", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.get_team_projects_service")
def test_get_team_projects_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/team/{current_user.id}/projects", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.create_project_service")
def test_create_project_success(
    mock_service, mock_user, current_user, project, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = project

    response = client.post(
        f"/api/team/{project.team_id}/project/new",
        json={"name": "Test project"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == project.id
    assert data["name"] == project.name
    assert data["team_id"] == project.team_id


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.create_project_service")
def test_create_project_not_found(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        f"/api/team/{current_user.id}/project/new",
        json={"name": "Test project"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.project_service.create_project_service")
def test_create_project_forbidden(
    mock_service, mock_user, current_user, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        f"/api/team/{current_user.id}/project/new",
        json={"name": "Test project"},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.get_team_tags_service")
def test_get_team_tags_not_found(
    mock_service, mock_user, current_user, team, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/team/{team.id}/tags", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.get_team_tags_service")
def test_get_team_tags_forbidden(
    mock_service, mock_user, current_user, team, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/team/{team.id}/tags", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.create_tag_service")
def test_create_team_tag_not_found(
    mock_service, mock_user, current_user, team, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.post(
        f"/api/team/{team.id}/tags/new",
        json={"name": "Backend", "color": "#3B82F6"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.create_tag_service")
def test_create_team_tag_forbidden(
    mock_service, mock_user, current_user, team, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.post(
        f"/api/team/{team.id}/tags/new",
        json={"name": "Backend", "color": "#3B82F6"},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.delete_tag_service")
def test_delete_team_tag_not_found(
    mock_service, mock_user, current_user, team, tag_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(
        f"/api/team/{team.id}/tags/{tag_obj.id}", headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.delete_tag_service")
def test_delete_team_tag_forbidden(
    mock_service, mock_user, current_user, team, tag_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(
        f"/api/team/{team.id}/tags/{tag_obj.id}", headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_relation_service")
def test_delete_task_relation_not_found(
    mock_service, mock_user, current_user, team, relation, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(
        f"/api/team/{team.id}/relation/{relation.id}", headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_relation_service")
def test_delete_task_relation_forbidden(
    mock_service, mock_user, current_user, team, relation, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(
        f"/api/team/{team.id}/relation/{relation.id}", headers=auth_headers
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.get_team_tags_service")
def test_get_team_tags_success(
    mock_service, mock_user, current_user, team, tag_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [tag_obj]

    response = client.get(f"/api/team/{team.id}/tags", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == tag_obj.id
    assert data[0]["name"] == tag_obj.name
    assert data[0]["color"] == tag_obj.color


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.create_tag_service")
def test_create_team_tag_success(
    mock_service, mock_user, current_user, team, tag_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = tag_obj

    response = client.post(
        f"/api/team/{team.id}/tags/new",
        json={"name": tag_obj.name, "color": tag_obj.color},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == tag_obj.id
    assert data["name"] == tag_obj.name
    assert data["color"] == tag_obj.color


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.tag_service.delete_tag_service")
def test_delete_team_tag_success(
    mock_service, mock_user, current_user, team, tag_obj, auth_headers, client
):
    mock_user.return_value = current_user

    response = client.delete(
        f"/api/team/{team.id}/tags/{tag_obj.id}", headers=auth_headers
    )

    assert response.status_code == 204
    mock_service.assert_called_once()


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.task_service.delete_task_relation_service")
def test_delete_task_relation_success(
    mock_service, mock_user, current_user, team, relation, auth_headers, client
):
    mock_user.return_value = current_user

    response = client.delete(
        f"/api/team/{team.id}/relation/{relation.id}", headers=auth_headers
    )

    assert response.status_code == 204
    mock_service.assert_called_once()
