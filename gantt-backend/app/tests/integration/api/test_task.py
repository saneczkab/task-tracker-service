def test_get_all_tasks_success(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    task_obj,
    auth_headers,
):
    response = client.get("/api/tasks/all", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == task_obj.id and fields["stream_id"] == stream_obj.id
        for fields in data
    )


def test_update_task_success(client, task_obj, user_team_obj, auth_headers):
    payload = {"name": "Renamed task"}
    response = client.patch(
        f"/api/task/{task_obj.id}", json=payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_obj.id
    assert data["name"] == payload["name"]


def test_update_task_not_found(client, auth_headers, user_obj):
    response = client.patch(
        "/api/task/999", json={"name": "test"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_update_task_forbidden(client, other_task_1_obj, auth_headers, user_obj):
    response = client.patch(
        f"/api/task/{other_task_1_obj.id}",
        json={"name": "test"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_task_success(client, task_obj, user_team_obj, auth_headers):
    response = client.delete(f"/api/task/{task_obj.id}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_task_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/task/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_task_forbidden(client, other_task_1_obj, auth_headers, user_obj):
    response = client.delete(f"/api/task/{other_task_1_obj.id}", headers=auth_headers)
    assert response.status_code == 403


def test_create_task_relation_success(
    client, task_obj, second_task_obj, connection_type_obj, auth_headers
):
    response = client.post(
        f"/api/task/{task_obj.id}/relation",
        json={"task_id": second_task_obj.id, "connection_id": connection_type_obj.id},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id_1"] == task_obj.id
    assert data["task_id_2"] == second_task_obj.id
    assert data["connection_id"] == connection_type_obj.id
    assert data["connection_name"] == connection_type_obj.name


def test_create_task_relation_not_found_when_task_missing(
    client, connection_type_obj, auth_headers
):
    response = client.post(
        "/api/task/999/relation",
        json={"task_id": 1000, "connection_id": connection_type_obj.id},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_task_relation_conflict_when_self_relation(
    client, task_obj, connection_type_obj, auth_headers
):
    response = client.post(
        f"/api/task/{task_obj.id}/relation",
        json={"task_id": task_obj.id, "connection_id": connection_type_obj.id},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_get_task_history_success_after_update(
    client,
    task_obj,
    user_team_obj,
    auth_headers,
):
    response_update = client.patch(
        f"/api/task/{task_obj.id}",
        json={"name": "test2"},
        headers=auth_headers,
    )
    assert response_update.status_code == 200

    response_history = client.get(
        f"/api/task/{task_obj.id}/history", headers=auth_headers
    )
    assert response_history.status_code == 200
    data = response_history.json()
    assert any(fields["field_name"] == "name" for fields in data)


def test_get_task_history_not_found(client, auth_headers, user_obj):
    response = client.get("/api/task/999/history", headers=auth_headers)
    assert response.status_code == 404


def test_get_task_history_forbidden(client, other_task_1_obj, auth_headers, user_obj):
    response = client.get(
        f"/api/task/{other_task_1_obj.id}/history", headers=auth_headers
    )
    assert response.status_code == 403


def test_delete_task_custom_field_success(
    client,
    task_obj,
    custom_field_obj,
    task_custom_field_value_obj,
    user_team_obj,
    auth_headers,
):
    response = client.delete(
        f"/api/task/{task_obj.id}/custom_fields/{custom_field_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


def test_delete_task_custom_field_not_found(
    client,
    task_obj,
    user_team_obj,
    auth_headers,
):
    response = client.delete(
        f"/api/task/{task_obj.id}/custom_fields/999",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_delete_task_custom_field_forbidden(
    client,
    other_task_1_obj,
    other_task_custom_field_value_obj,
    other_custom_field_obj,
    auth_headers,
    user_obj,
):
    response = client.delete(
        f"/api/task/{other_task_1_obj.id}/custom_fields/{other_custom_field_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403
