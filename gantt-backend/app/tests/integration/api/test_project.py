def test_update_project_success(client, project_obj, user_team_obj, auth_headers):
    payload = {"name": "Renamed project"}

    response = client.patch(
        f"/api/project/{project_obj.id}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_obj.id
    assert data["name"] == payload["name"]


def test_update_project_not_exists(client, auth_headers, user_obj):
    response = client.patch(
        "/api/project/999", json={"name": "test not exist"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_update_project_forbidden(client, other_project_obj, auth_headers, user_obj):
    response = client.patch(
        f"/api/project/{other_project_obj.id}",
        json={"name": "test"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_project_success(client, project_obj, user_team_obj, auth_headers):
    response = client.delete(f"/api/project/{project_obj.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_project_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/project/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_project_forbidden(client, other_project_obj, auth_headers, user_obj):
    response = client.delete(
        f"/api/project/{other_project_obj.id}", headers=auth_headers
    )
    assert response.status_code == 403


def test_get_project_streams_success(
    client,
    project_obj,
    stream_obj,
    user_team_obj,
    auth_headers,
):
    response = client.get(
        f"/api/project/{project_obj.id}/streams", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == stream_obj.id and fields["project_id"] == project_obj.id
        for fields in data
    )


def test_get_project_streams_not_found(client, auth_headers, user_obj):
    response = client.get("/api/project/999/streams", headers=auth_headers)
    assert response.status_code == 404


def test_get_project_streams_forbidden(
    client, other_project_obj, auth_headers, user_obj
):
    response = client.get(
        f"/api/project/{other_project_obj.id}/streams", headers=auth_headers
    )
    assert response.status_code == 403


def test_create_stream_success(client, project_obj, user_team_obj, auth_headers):
    response = client.post(
        f"/api/project/{project_obj.id}/stream/new",
        json={"name": "New stream"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_obj.id
    assert data["name"] == "New stream"


def test_create_stream_conflict_when_same_name_in_project(
    client,
    project_obj,
    stream_obj,
    user_team_obj,
    auth_headers,
):
    response = client.post(
        f"/api/project/{project_obj.id}/stream/new",
        json={"name": stream_obj.name},
        headers=auth_headers,
    )
    assert response.status_code == 409


def test_create_stream_not_found(client, auth_headers, user_obj):
    response = client.post(
        "/api/project/999/stream/new",
        json={"name": "New stream"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_stream_forbidden(client, other_project_obj, auth_headers, user_obj):
    response = client.post(
        f"/api/project/{other_project_obj.id}/stream/new",
        json={"name": "New stream"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_get_project_tasks_success(
    client,
    project_obj,
    task_obj,
    user_team_obj,
    auth_headers,
):
    response = client.get(f"/api/project/{project_obj.id}/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == task_obj.id and fields["stream_id"] == task_obj.stream_id
        for fields in data
    )


def test_get_project_tasks_not_found(client, auth_headers, user_obj):
    response = client.get("/api/project/999/tasks", headers=auth_headers)
    assert response.status_code == 404


def test_get_project_tasks_forbidden(client, other_project_obj, auth_headers, user_obj):
    response = client.get(
        f"/api/project/{other_project_obj.id}/tasks", headers=auth_headers
    )
    assert response.status_code == 403
