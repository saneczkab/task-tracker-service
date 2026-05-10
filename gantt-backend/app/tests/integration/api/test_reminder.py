from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock


def test_get_task_reminders_success(
    client, task_obj, reminder_obj, auth_headers, user_team_obj
):
    response = client.get(f"/api/tasks/{task_obj.id}/reminders", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(
        fields["id"] == reminder_obj.id and fields["task_id"] == task_obj.id
        for fields in data
    )


def test_get_task_reminders_not_found(client, auth_headers, user_obj):
    response = client.get("/api/tasks/999/reminders", headers=auth_headers)
    assert response.status_code == 404


def test_get_task_reminders_forbidden(client, other_task_1_obj, auth_headers, user_obj):
    response = client.get(
        f"/api/tasks/{other_task_1_obj.id}/reminders", headers=auth_headers
    )
    assert response.status_code == 403


def test_create_reminder_success(client, task_obj, auth_headers, user_team_obj):
    scheduler_mock = MagicMock()
    scheduler_mock.get_job.return_value = None
    remind_at = (datetime.now() + timedelta(days=1)).isoformat()
    with patch("app.api.reminder.scheduler", scheduler_mock):
        response = client.post(
            f"/api/tasks/{task_obj.id}/reminders",
            json={"remind_at": remind_at},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_obj.id


def test_create_reminder_validation_error_past_datetime(
    client, task_obj, auth_headers, user_team_obj
):
    remind_at = (datetime.now() - timedelta(days=1)).isoformat()
    response = client.post(
        f"/api/tasks/{task_obj.id}/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_reminder_not_found(client, auth_headers, user_obj):
    remind_at = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/tasks/999/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_reminder_forbidden(client, other_task_1_obj, auth_headers, user_obj):
    remind_at = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post(
        f"/api/tasks/{other_task_1_obj.id}/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )
    assert response.status_code == 403


@patch("app.api.reminder.scheduler")
def test_update_reminder_success(scheduler, client, reminder_obj, auth_headers):
    scheduler.get_job.return_value = None
    new_time = (datetime.now() + timedelta(days=2)).isoformat()

    response = client.patch(
        f"/api/tasks/reminders/{reminder_obj.id}",
        json={"remind_at": new_time},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reminder_obj.id


def test_update_reminder_not_found(client, auth_headers, user_obj):
    new_time = (datetime.now() + timedelta(days=2)).isoformat()
    response = client.patch(
        "/api/tasks/reminders/999",
        json={"remind_at": new_time},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_reminder_forbidden(
    client, foreign_reminder_obj, auth_headers, user_obj
):
    new_time = (datetime.now() + timedelta(days=2)).isoformat()
    response = client.patch(
        f"/api/tasks/reminders/{foreign_reminder_obj.id}",
        json={"remind_at": new_time},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_reminder_success(client, reminder_obj, auth_headers):
    response = client.delete(
        f"/api/tasks/reminders/{reminder_obj.id}", headers=auth_headers
    )
    assert response.status_code == 204


def test_delete_reminder_not_found(client, auth_headers, user_obj):
    response = client.delete("/api/tasks/reminders/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_reminder_forbidden(
    client, foreign_reminder_obj, auth_headers, user_obj
):
    response = client.delete(
        f"/api/tasks/reminders/{foreign_reminder_obj.id}",
        headers=auth_headers,
    )
    assert response.status_code == 403
