def test_check_email_exists_true(client, user_obj):
    response = client.post("/api/check-email", params={"email": user_obj.email})
    assert response.status_code == 200
    assert response.json() == {"exists": True}


def test_check_email_not_exists(client):
    response = client.post("/api/check-email", params={"email": "notexist@example.com"})
    assert response.status_code == 200
    assert response.json() == {"exists": False}


def test_register_success(client):
    response = client.post(
        "/api/register",
        params={
            "email": "new@example.com",
            "nickname": "new_user",
            "password": "password",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


def test_register_conflict_email(client, user_obj):
    response = client.post(
        "/api/register",
        params={
            "email": user_obj.email,
            "nickname": "another_nick",
            "password": "password",
        },
    )
    assert response.status_code == 409


def test_register_conflict_nickname(client, user_obj):
    response = client.post(
        "/api/register",
        params={
            "email": "another@example.com",
            "nickname": user_obj.nickname,
            "password": "password",
        },
    )
    assert response.status_code == 409


def test_login(client, user_obj):
    response = client.post(
        "/api/login",
        params={"email": user_obj.email, "password": "test_password"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


def test_login_unauthorized(client, user_obj):
    response = client.post(
        "/api/login",
        params={"email": user_obj.email, "password": "wrong_password"},
    )
    assert response.status_code == 401
