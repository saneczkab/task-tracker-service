from datetime import datetime, timedelta
from unittest.mock import DEFAULT, patch

from app.core import exception


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.get_task_reminders_service")
def test_get_task_reminders_success(
    mock_service, mock_user, current_user, task_obj, reminder_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.return_value = [reminder_obj]

    response = client.get(f"/api/tasks/{task_obj.id}/reminders", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == reminder_obj.id
    assert data[0]["task_id"] == reminder_obj.task_id
    assert data[0]["user_id"] == reminder_obj.user_id


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.get_task_reminders_service")
def test_get_task_reminders_not_found(
    mock_service, mock_user, current_user, task_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.get(f"/api/tasks/{task_obj.id}/reminders", headers=auth_headers)

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.get_task_reminders_service")
def test_get_task_reminders_forbidden(
    mock_service, mock_user, current_user, task_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.get(f"/api/tasks/{task_obj.id}/reminders", headers=auth_headers)

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.create_reminder_service")
@patch("app.api.reminder.scheduler.add_job")
def test_create_reminder_success(
    mock_add_job,
    mock_service,
    mock_user,
    current_user,
    task_obj,
    reminder_obj,
    auth_headers,
    client,
):
    mock_user.return_value = current_user
    mock_service.return_value = reminder_obj

    remind_at = (datetime.now() + timedelta(hours=2)).isoformat()
    response = client.post(
        f"/api/tasks/{task_obj.id}/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reminder_obj.id
    assert data["task_id"] == reminder_obj.task_id
    assert data["user_id"] == reminder_obj.user_id
    mock_add_job.assert_called_once()


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.create_reminder_service")
def test_create_reminder_conflict(
    mock_service, mock_user, current_user, task_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    remind_at = (datetime.now() + timedelta(hours=2)).isoformat()
    response = client.post(
        f"/api/tasks/{task_obj.id}/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 400


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.create_reminder_service")
def test_create_reminder_not_found(
    mock_service, mock_user, current_user, task_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    remind_at = (datetime.now() + timedelta(hours=2)).isoformat()
    response = client.post(
        f"/api/tasks/{task_obj.id}/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.create_reminder_service")
def test_create_reminder_forbidden(
    mock_service, mock_user, current_user, task_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    remind_at = (datetime.now() + timedelta(hours=2)).isoformat()
    response = client.post(
        f"/api/tasks/{task_obj.id}/reminders",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch.multiple(
    "app.api.reminder.scheduler", get_job=DEFAULT, remove_job=DEFAULT, add_job=DEFAULT
)
@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.update_reminder_service")
def test_update_reminder_success_reschedules_job(
    mock_service,
    mock_user,
    current_user,
    reminder_obj,
    auth_headers,
    client,
    **scheduler_mocks,
):
    mock_user.return_value = current_user
    mock_service.return_value = reminder_obj
    scheduler_mocks["get_job"].return_value = object()

    remind_at = (datetime.now() + timedelta(hours=3)).isoformat()
    response = client.patch(
        f"/api/tasks/reminders/{reminder_obj.id}",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 200
    scheduler_mocks["remove_job"].assert_called_once_with(str(reminder_obj.id))
    scheduler_mocks["add_job"].assert_called_once()


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.update_reminder_service")
def test_update_reminder_not_found(
    mock_service, mock_user, current_user, reminder_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    remind_at = (datetime.now() + timedelta(hours=3)).isoformat()
    response = client.patch(
        f"/api/tasks/reminders/{reminder_obj.id}",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.update_reminder_service")
def test_update_reminder_forbidden(
    mock_service, mock_user, current_user, reminder_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    remind_at = (datetime.now() + timedelta(hours=3)).isoformat()
    response = client.patch(
        f"/api/tasks/reminders/{reminder_obj.id}",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 403


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.update_reminder_service")
def test_update_reminder_conflict(
    mock_service, mock_user, current_user, reminder_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ConflictError()

    remind_at = (datetime.now() + timedelta(hours=3)).isoformat()
    response = client.patch(
        f"/api/tasks/reminders/{reminder_obj.id}",
        json={"remind_at": remind_at},
        headers=auth_headers,
    )

    assert response.status_code == 400


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.delete_reminder_service")
@patch.multiple("app.api.reminder.scheduler", get_job=DEFAULT, remove_job=DEFAULT)
def test_delete_reminder_success_removes_job(
    mock_service,
    mock_user,
    current_user,
    reminder_obj,
    auth_headers,
    client,
    **scheduler_mocks,
):
    mock_user.return_value = current_user
    scheduler_mocks["get_job"].return_value = object()

    response = client.delete(
        f"/api/tasks/reminders/{reminder_obj.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    mock_service.assert_called_once()
    scheduler_mocks["remove_job"].assert_called_once_with(str(reminder_obj.id))


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.delete_reminder_service")
def test_delete_reminder_not_found(
    mock_service, mock_user, current_user, reminder_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.NotFoundError()

    response = client.delete(
        f"/api/tasks/reminders/{reminder_obj.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.services.user_service.get_current_user_service")
@patch("app.services.reminder_service.delete_reminder_service")
def test_delete_reminder_forbidden(
    mock_service, mock_user, current_user, reminder_obj, auth_headers, client
):
    mock_user.return_value = current_user
    mock_service.side_effect = exception.ForbiddenError()

    response = client.delete(
        f"/api/tasks/reminders/{reminder_obj.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403
