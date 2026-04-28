from app.tests.factories import build_task_relation


def test_create_team_success(client, auth_headers, user_obj):
    response = client.post(
        "/api/team/new", json={"name": "New team"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New team"


def test_update_team_success(client, team_obj, user_team_obj, auth_headers):
    response = client.patch(
        f"/api/team/{team_obj.id}",
        json={"name": "test2"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == team_obj.id
    assert data["name"] == "test2"


def test_update_team_not_found(client, auth_headers, user_obj):
    response = client.patch(
        "/api/team/999", json={"name": "test"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_update_team_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.patch(
        f"/api/team/{other_team_obj.id}", json={"name": "test"}, headers=auth_headers
    )
    assert response.status_code == 403


def test_delete_team_success(client, team_obj, user_team_obj, auth_headers):
    response = client.delete(f"/api/team/{team_obj.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_team_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/team/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_team_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.delete(f"/api/team/{other_team_obj.id}", headers=auth_headers)
    assert response.status_code == 403


def test_get_team_users_success(
    client, team_obj, user_obj, user_team_obj, auth_headers
):
    response = client.get(f"/api/team/{team_obj.id}/users", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == user_obj.id and fields["email"] == user_obj.email
        for fields in data
    )


def test_get_team_users_not_found(client, auth_headers, user_obj):
    response = client.get("/api/team/999/users", headers=auth_headers)
    assert response.status_code == 404


def test_get_team_users_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.get(f"/api/team/{other_team_obj.id}/users", headers=auth_headers)
    assert response.status_code == 403


def test_get_team_projects_success(
    client, team_obj, project_obj, user_team_obj, auth_headers
):
    response = client.get(f"/api/team/{team_obj.id}/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == project_obj.id and fields["team_id"] == team_obj.id
        for fields in data
    )


def test_get_team_projects_not_found(client, auth_headers, user_obj):
    response = client.get("/api/team/999/projects", headers=auth_headers)
    assert response.status_code == 404


def test_get_team_projects_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.get(
        f"/api/team/{other_team_obj.id}/projects", headers=auth_headers
    )
    assert response.status_code == 403


def test_get_team_tags_returns_empty_list(
    client, team_obj, user_team_obj, auth_headers
):
    response = client.get(f"/api/team/{team_obj.id}/tags", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_create_team_tag_success(client, team_obj, user_team_obj, auth_headers):
    response = client.post(
        f"/api/team/{team_obj.id}/tags/new",
        json={"name": "Tag1", "color": "#AABBCC"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tag1"
    assert data["color"] == "#AABBCC"


def test_create_team_tag_not_found(client, auth_headers, user_obj):
    response = client.post(
        "/api/team/999/tags/new",
        json={"name": "Tag1", "color": "#AABBCC"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_team_tag_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.post(
        f"/api/team/{other_team_obj.id}/tags/new",
        json={"name": "Tag1", "color": "#AABBCC"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_team_tag_success(
    client, team_obj, tag_obj, user_team_obj, auth_headers
):
    response = client.delete(
        f"/api/team/{team_obj.id}/tags/{tag_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


def test_delete_team_tag_not_found(client, team_obj, user_team_obj, auth_headers):
    response = client.delete(f"/api/team/{team_obj.id}/tags/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_team_tag_forbidden(
    client,
    other_team_obj,
    other_project_obj,
    other_stream_obj,
    other_tag_obj,
    auth_headers,
    user_obj,
):
    response = client.delete(
        f"/api/team/{other_team_obj.id}/tags/{other_tag_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_task_relation_success(
    client,
    auth_headers,
    team_obj,
    task_obj,
    second_task_obj,
    connection_type_obj,
    user_team_obj,
    db_session,
):
    relation = build_task_relation(
        relation_id=42,
        task_id_1=task_obj.id,
        task_id_2=second_task_obj.id,
        connection_id=connection_type_obj.id,
    )
    db_session.add(relation)
    db_session.commit()

    response = client.delete(
        f"/api/team/{team_obj.id}/relation/{relation.id}", headers=auth_headers
    )
    assert response.status_code == 204


def test_delete_task_relation_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/team/42/relation/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_task_relation_forbidden(
    client,
    auth_headers,
    user_obj,
    other_team_obj,
    other_project_obj,
    other_stream_obj,
    other_relation_obj,
):
    response = client.delete(
        f"/api/team/{other_team_obj.id}/relation/{other_relation_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_create_project_success(client, team_obj, user_team_obj, auth_headers):
    response = client.post(
        f"/api/team/{team_obj.id}/project/new",
        json={"name": "New project"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New project"
    assert data["team_id"] == team_obj.id


def test_create_project_not_found(client, auth_headers, user_obj):
    response = client.post(
        "/api/team/999/project/new",
        json={"name": "New project"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_project_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.post(
        f"/api/team/{other_team_obj.id}/project/new",
        json={"name": "New project"},
        headers=auth_headers,
    )
    assert response.status_code == 403
