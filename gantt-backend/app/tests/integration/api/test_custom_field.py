def test_double_create_custom_field(
    client,
    team_obj,
    user_team_obj,
    auth_headers,
):
    payload = {"name": "test", "type": "string"}

    first = client.post(
        f"/api/teams/{team_obj.id}/custom_fields/",
        json=payload,
        headers=auth_headers,
    )
    assert first.status_code == 200
    first_id = first.json()["id"]

    second = client.post(
        f"/api/teams/{team_obj.id}/custom_fields/",
        json=payload,
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["id"] == first_id


def test_create_custom_field_forbidden(client, other_team_obj, auth_headers, user_obj):
    payload = {"name": "test", "type": "string"}

    response = client.post(
        f"/api/teams/{other_team_obj.id}/custom_fields/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_read_custom_fields_success(
    client,
    team_obj,
    user_team_obj,
    custom_field_obj,
    auth_headers,
):
    response = client.get(
        f"/api/teams/{team_obj.id}/custom_fields/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == custom_field_obj.id and fields["name"] == custom_field_obj.name
        for fields in data
    )


def test_read_custom_fields_forbidden(client, other_team_obj, auth_headers, user_obj):
    response = client.get(
        f"/api/teams/{other_team_obj.id}/custom_fields/",
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_update_custom_field_success(
    client, custom_field_obj, user_team_obj, auth_headers
):
    payload = {"name": "test2", "type": "string"}

    response = client.put(
        f"/api/custom_fields/{custom_field_obj.id}/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == custom_field_obj.id
    assert data["name"] == payload["name"]
    assert data["type"] == payload["type"]


def test_update_custom_field_not_found(client, auth_headers, user_obj):
    payload = {"name": "test2", "type": "string"}
    response = client.put("/api/custom_fields/999/", json=payload, headers=auth_headers)
    assert response.status_code == 404


def test_update_custom_field_forbidden(
    client,
    other_custom_field_obj,
    other_team_obj,
    auth_headers,
    user_obj,
):
    payload = {"name": "test2", "type": "string"}
    response = client.put(
        f"/api/custom_fields/{other_custom_field_obj.id}/",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_custom_field_success(
    client, custom_field_obj, user_team_obj, auth_headers
):
    response = client.delete(
        f"/api/custom_fields/{custom_field_obj.id}/", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == custom_field_obj.id


def test_delete_custom_field_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/custom_fields/999/", headers=auth_headers)
    assert response.status_code == 404


def test_delete_custom_field_forbidden(
    client,
    other_custom_field_obj,
    other_team_obj,
    auth_headers,
    user_obj,
):
    response = client.delete(
        f"/api/custom_fields/{other_custom_field_obj.id}/", headers=auth_headers
    )
    assert response.status_code == 403
