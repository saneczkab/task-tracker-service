from app.tests.factories import build_goal


def test_get_stream_goals_success(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    goal_obj,
    auth_headers,
):
    response = client.get(f"/api/stream/{stream_obj.id}/goals", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == goal_obj.id
    assert data[0]["name"] == goal_obj.name


def test_get_stream_goals_not_found(client, user_obj, auth_headers):
    response = client.get("/api/stream/999/goals", headers=auth_headers)

    assert response.status_code == 404


def test_get_stream_goals_forbidden(
    client,
    user_obj,
    other_team_obj,
    other_project_obj,
    other_stream_obj,
    auth_headers,
):
    response = client.get(
        f"/api/stream/{other_stream_obj.id}/goals", headers=auth_headers
    )

    assert response.status_code == 403


def test_create_goal_success(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    auth_headers,
):
    payload = {"name": "Test", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        f"/api/stream/{stream_obj.id}/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert data["stream_id"] == stream_obj.id


def test_create_goal_not_found(client, user_obj, auth_headers):
    payload = {"name": "Test", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        "/api/stream/999/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 404


def test_create_goal_forbidden(
    client,
    user_obj,
    other_team_obj,
    other_project_obj,
    other_stream_obj,
    auth_headers,
):
    payload = {"name": "Test goal", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        f"/api/stream/{other_stream_obj.id}/goal/new",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_create_goal_conflict(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    db_session,
    auth_headers,
):
    existing_goal = build_goal(
        goal_id=42,
        name="Test",
        stream_id=stream_obj.id,
        position=1,
    )
    db_session.add(existing_goal)
    db_session.commit()

    payload = {"name": "Test", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        f"/api/stream/{stream_obj.id}/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 409


def test_update_goal_success(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    goal_obj,
    auth_headers,
):
    payload = {"name": "test2"}

    response = client.patch(
        f"/api/goal/{goal_obj.id}", json=payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == goal_obj.id
    assert data["name"] == payload["name"]


def test_update_goal_not_found(client, user_obj, auth_headers):
    payload = {"name": "Test"}

    response = client.patch("/api/goal/999", json=payload, headers=auth_headers)

    assert response.status_code == 404


def test_update_goal_forbidden(
    client,
    user_obj,
    other_team_obj,
    other_project_obj,
    other_stream_obj,
    other_goal_obj,
    auth_headers,
):
    payload = {"name": "Test"}

    response = client.patch(
        f"/api/goal/{other_goal_obj.id}", json=payload, headers=auth_headers
    )

    assert response.status_code == 403


def test_update_goal_conflict(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    db_session,
    auth_headers,
):
    existing_goal = build_goal(
        goal_id=42,
        name="Test",
        stream_id=stream_obj.id,
        position=1,
    )
    db_session.add(existing_goal)

    second_goal = build_goal(
        goal_id=43,
        name="Test 2",
        stream_id=stream_obj.id,
        position=2,
    )
    db_session.add(second_goal)
    db_session.commit()

    payload = {"name": "Test"}

    response = client.patch(
        f"/api/goal/{second_goal.id}", json=payload, headers=auth_headers
    )

    assert response.status_code == 409


def test_delete_goal_success(
    client,
    user_obj,
    team_obj,
    user_team_obj,
    project_obj,
    stream_obj,
    goal_obj,
    auth_headers,
):
    response = client.delete(f"/api/goal/{goal_obj.id}", headers=auth_headers)

    assert response.status_code == 204


def test_delete_goal_not_found(client, user_obj, auth_headers):
    response = client.delete("/api/goal/999", headers=auth_headers)

    assert response.status_code == 404


def test_delete_goal_forbidden(
    client,
    user_obj,
    other_team_obj,
    other_project_obj,
    other_stream_obj,
    other_goal_obj,
    auth_headers,
):
    response = client.delete(f"/api/goal/{other_goal_obj.id}", headers=auth_headers)

    assert response.status_code == 403
