from datetime import datetime
import pytest

from app.models import (
    goal as goal_model,
    stream as stream_model,
    project as project_model,
    team as team_model,
)


@pytest.fixture
def goal_obj(seed_db):
    g = goal_model.Goal(
        id=42,
        name="Test",
        description="",
        start_date=None,
        deadline=datetime(2026, 12, 31),
        stream_id=42,
        position=1,
    )
    seed_db.add(g)
    seed_db.commit()
    return g


def test_get_stream_goals_success(client, seed_db, goal_obj, auth_headers):
    response = client.get("/api/stream/42/goals", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 42
    assert data[0]["name"] == "Test"


def test_get_stream_goals_not_found(client, seed_db, auth_headers):
    response = client.get("/api/stream/999/goals", headers=auth_headers)

    assert response.status_code == 404


def test_get_stream_goals_forbidden(client, seed_db, auth_headers):

    other_team = team_model.Team(id=99, name="Other team")
    seed_db.add(other_team)
    other_project = project_model.Project(id=99, name="Other project", team_id=99)
    seed_db.add(other_project)
    other_stream = stream_model.Stream(id=99, name="Other stream", project_id=99)
    seed_db.add(other_stream)
    seed_db.commit()

    response = client.get("/api/stream/99/goals", headers=auth_headers)

    assert response.status_code == 403


def test_create_goal_success(client, seed_db, auth_headers):
    payload = {"name": "Test", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        "/api/stream/42/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert data["stream_id"] == 42


def test_create_goal_not_found(client, seed_db, auth_headers):
    payload = {"name": "Test", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        "/api/stream/999/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 404


def test_create_goal_forbidden(client, seed_db, auth_headers):
    other_team = team_model.Team(id=99, name="Other team")
    seed_db.add(other_team)
    other_project = project_model.Project(id=99, name="Other project", team_id=99)
    seed_db.add(other_project)
    other_stream = stream_model.Stream(id=99, name="Other stream", project_id=99)
    seed_db.add(other_stream)
    seed_db.commit()

    payload = {"name": "Test goal", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        "/api/stream/99/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 403


def test_create_goal_conflict(client, seed_db, goal_obj, auth_headers):
    payload = {"name": "Test", "deadline": "2026-12-31T00:00:00"}

    response = client.post(
        "/api/stream/42/goal/new", json=payload, headers=auth_headers
    )

    assert response.status_code == 409


def test_update_goal_success(client, seed_db, goal_obj, auth_headers):
    payload = {"name": "Test"}

    response = client.patch("/api/goal/42", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "Test"


def test_update_goal_not_found(client, seed_db, auth_headers):
    payload = {"name": "Test"}

    response = client.patch("/api/goal/999", json=payload, headers=auth_headers)

    assert response.status_code == 404


def test_update_goal_forbidden(client, seed_db, auth_headers):
    from app.models import (
        stream as stream_model,
        project as project_model,
        team as team_model,
    )

    other_team = team_model.Team(id=99, name="Other team")
    seed_db.add(other_team)
    other_project = project_model.Project(id=99, name="Other project", team_id=99)
    seed_db.add(other_project)
    other_stream = stream_model.Stream(id=99, name="Other stream", project_id=99)
    seed_db.add(other_stream)
    other_goal = goal_model.Goal(
        id=99,
        name="Other Goal",
        deadline=datetime(2026, 12, 31),
        stream_id=99,
        position=1,
    )
    seed_db.add(other_goal)
    seed_db.commit()

    payload = {"name": "Test"}

    response = client.patch("/api/goal/99", json=payload, headers=auth_headers)

    assert response.status_code == 403


def test_update_goal_conflict(client, seed_db, goal_obj, auth_headers):
    second_goal = goal_model.Goal(
        id=43,
        name="Test 2",
        deadline=datetime(2026, 12, 31),
        stream_id=42,
        position=2,
    )
    seed_db.add(second_goal)
    seed_db.commit()

    payload = {"name": "Test"}

    response = client.patch("/api/goal/43", json=payload, headers=auth_headers)

    assert response.status_code == 409


def test_delete_goal_success(client, seed_db, goal_obj, auth_headers):
    response = client.delete("/api/goal/42", headers=auth_headers)

    assert response.status_code == 204


def test_delete_goal_not_found(client, seed_db, auth_headers):
    response = client.delete("/api/goal/999", headers=auth_headers)

    assert response.status_code == 404


def test_delete_goal_forbidden(client, seed_db, auth_headers):
    from app.models import (
        stream as stream_model,
        project as project_model,
        team as team_model,
    )

    other_team = team_model.Team(id=99, name="Other team")
    seed_db.add(other_team)
    other_project = project_model.Project(id=99, name="Other project", team_id=99)
    seed_db.add(other_project)
    other_stream = stream_model.Stream(id=99, name="Other stream", project_id=99)
    seed_db.add(other_stream)
    other_goal = goal_model.Goal(
        id=99,
        name="Other goal",
        deadline=datetime(2026, 12, 31),
        stream_id=99,
        position=1,
    )
    seed_db.add(other_goal)
    seed_db.commit()

    response = client.delete("/api/goal/99", headers=auth_headers)

    assert response.status_code == 403
