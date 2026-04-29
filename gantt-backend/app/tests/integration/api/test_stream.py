def test_get_stream_success(client, stream_obj, user_team_obj, auth_headers):
    response = client.get(f"/api/stream/{stream_obj.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == stream_obj.id
    assert data["project_id"] == stream_obj.project_id


def test_get_stream_not_found(client, auth_headers, user_obj):
    response = client.get("/api/stream/999", headers=auth_headers)
    assert response.status_code == 404


def test_get_stream_forbidden(client, other_stream_obj, auth_headers, user_obj):
    response = client.get(f"/api/stream/{other_stream_obj.id}", headers=auth_headers)
    assert response.status_code == 403


def test_update_stream_success(client, stream_obj, user_team_obj, auth_headers):
    payload = {"name": "Renamed stream"}

    response = client.patch(
        f"/api/stream/{stream_obj.id}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == stream_obj.id
    assert data["name"] == payload["name"]


def test_update_stream_not_found(client, auth_headers, user_obj):
    response = client.patch(
        "/api/stream/999", json={"name": "not-exists"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_update_stream_forbidden(client, other_stream_obj, auth_headers, user_obj):
    response = client.patch(
        f"/api/stream/{other_stream_obj.id}",
        json={"name": "test"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_stream_success(client, stream_obj, user_team_obj, auth_headers):
    response = client.delete(f"/api/stream/{stream_obj.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_stream_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/stream/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_stream_forbidden(client, other_stream_obj, auth_headers, user_obj):
    response = client.delete(f"/api/stream/{other_stream_obj.id}", headers=auth_headers)
    assert response.status_code == 403


def test_get_stream_tasks_success(
    client,
    stream_obj,
    task_obj,
    user_team_obj,
    auth_headers,
):
    response = client.get(f"/api/stream/{stream_obj.id}/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == task_obj.id and fields["stream_id"] == stream_obj.id
        for fields in data
    )


def test_get_stream_tasks_not_found(client, auth_headers, user_obj):
    response = client.get("/api/stream/999/tasks", headers=auth_headers)
    assert response.status_code == 404


def test_get_stream_tasks_forbidden(client, other_stream_obj, auth_headers, user_obj):
    response = client.get(
        f"/api/stream/{other_stream_obj.id}/tasks", headers=auth_headers
    )
    assert response.status_code == 403


def test_create_task_success(client, stream_obj, user_team_obj, auth_headers):
    payload = {"name": "New task"}
    response = client.post(
        f"/api/stream/{stream_obj.id}/task/new",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["stream_id"] == stream_obj.id


def test_create_task_not_found(client, auth_headers, user_obj):
    response = client.post(
        "/api/stream/999/task/new",
        json={"name": "New task"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_task_forbidden(client, other_stream_obj, auth_headers, user_obj):
    response = client.post(
        f"/api/stream/{other_stream_obj.id}/task/new",
        json={"name": "New task"},
        headers=auth_headers,
    )
    assert response.status_code == 403
