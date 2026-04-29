def test_get_user_by_token_success(
    client,
    auth_headers,
    user_obj,
    team_obj,
    user_team_obj,
):
    response = client.get("/api/user_by_token", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_obj.id
    assert data["email"] == user_obj.email
    assert data["nickname"] == user_obj.nickname

    assert any(
        fields["id"] == team_obj.id and fields["name"] == team_obj.name
        for fields in data["teams"]
    )


def test_get_user_by_token_not_found_when_user_missing(client, auth_headers):
    response = client.get("/api/user_by_token", headers=auth_headers)
    assert response.status_code == 404


def test_get_user_success(client, auth_headers, user_obj, team_obj, user_team_obj):
    response = client.get(f"/api/user/{user_obj.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_obj.id
    assert data["email"] == user_obj.email
    assert data["nickname"] == user_obj.nickname
    assert any(fields["id"] == team_obj.id for fields in data["teams"])


def test_get_user_forbidden_when_requesting_other_user(
    client,
    auth_headers,
    user_obj,
    second_user_obj,
):
    response = client.get(f"/api/user/{second_user_obj.id}", headers=auth_headers)
    assert response.status_code == 403
