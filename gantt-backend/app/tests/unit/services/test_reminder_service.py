from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.services.reminder_service import (
    create_reminder_service,
    delete_reminder_service,
    get_task_reminders_service,
    get_user_reminders_service,
    update_reminder_service,
)


@patch("app.services.reminder_service.reminder_crud.get_reminders_by_user")
def test_get_user_reminders_service_success(mock_get_reminders_by_user, mock_db, ids):
    expected = [Mock(), Mock()]
    mock_get_reminders_by_user.return_value = expected

    result = get_user_reminders_service(mock_db, ids.user_id)

    mock_get_reminders_by_user.assert_called_once_with(mock_db, ids.user_id)
    assert result is expected


@patch("app.services.reminder_service.reminder_crud.get_reminders_by_task_and_user")
@patch("app.services.reminder_service.permissions.check_task_access")
def test_get_task_reminders_service_success(
    mock_check_task_access, mock_get_reminders, mock_db, ids
):
    task_obj = Mock(id=ids.task_id)
    expected = [Mock()]
    mock_check_task_access.return_value = (task_obj, Mock(), Mock(), Mock())
    mock_get_reminders.return_value = expected

    result = get_task_reminders_service(mock_db, ids.task_id, ids.user_id)

    mock_check_task_access.assert_called_once_with(mock_db, ids.task_id, ids.user_id)
    mock_get_reminders.assert_called_once_with(mock_db, ids.task_id, ids.user_id)
    assert result is expected


@patch("app.services.reminder_service.reminder_crud.create_reminder")
@patch("app.services.reminder_service.permissions.check_task_access")
def test_create_reminder_service_success(
    mock_check_task_access, mock_create_reminder, mock_db, ids
):
    remind_at = datetime.now() + timedelta(hours=2)
    reminder_data = Mock(remind_at=remind_at)
    created_reminder = Mock(id=ids.goal_id, remind_at=remind_at)
    mock_check_task_access.return_value = (Mock(id=ids.task_id), Mock(), Mock(), Mock())
    mock_create_reminder.return_value = created_reminder

    result = create_reminder_service(mock_db, ids.task_id, ids.user_id, reminder_data)

    mock_check_task_access.assert_called_once_with(mock_db, ids.task_id, ids.user_id)
    mock_create_reminder.assert_called_once_with(
        mock_db,
        task_id=ids.task_id,
        user_id=ids.user_id,
        remind_at=remind_at,
    )
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(created_reminder)
    assert result is created_reminder


@patch("app.services.reminder_service.reminder_crud.create_reminder")
@patch("app.services.reminder_service.permissions.check_task_access")
def test_create_reminder_service_conflict_when_remind_at_in_past(
    mock_check_task_access, mock_create_reminder, mock_db, ids
):
    reminder_data = Mock(remind_at=datetime(2000, 1, 1, 10, 0, 0))
    mock_check_task_access.return_value = (Mock(id=ids.task_id), Mock(), Mock(), Mock())

    with pytest.raises(exception.ConflictError):
        create_reminder_service(mock_db, ids.task_id, ids.user_id, reminder_data)

    mock_create_reminder.assert_not_called()


@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
@patch("app.services.reminder_service.reminder_crud.update_reminder")
def test_update_reminder_service_success(
    mock_update_reminder, mock_get_reminder_by_id, mock_db, ids
):
    remind_at = datetime.now() + timedelta(hours=3)
    reminder_data = Mock(remind_at=remind_at)
    reminder_obj = Mock(id=ids.goal_id, user_id=ids.user_id)
    updated = Mock(id=reminder_obj.id, remind_at=remind_at)
    mock_get_reminder_by_id.return_value = reminder_obj
    mock_update_reminder.return_value = updated

    result = update_reminder_service(
        mock_db, reminder_obj.id, ids.user_id, reminder_data
    )

    mock_get_reminder_by_id.assert_called_once_with(mock_db, reminder_obj.id)
    mock_update_reminder.assert_called_once_with(mock_db, reminder_obj, reminder_data)
    assert result is updated


@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
@patch("app.services.reminder_service.reminder_crud.update_reminder")
def test_update_reminder_service_not_found(
    mock_update_reminder, mock_get_reminder_by_id, mock_db, ids
):
    reminder_data = Mock(remind_at=datetime.now() + timedelta(hours=1))
    mock_get_reminder_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_reminder_service(mock_db, ids.goal_id, ids.user_id, reminder_data)

    mock_update_reminder.assert_not_called()


@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
@patch("app.services.reminder_service.reminder_crud.update_reminder")
def test_update_reminder_service_forbidden(
    mock_update_reminder, mock_get_reminder_by_id, mock_db, ids
):
    reminder_data = Mock(remind_at=datetime.now() + timedelta(hours=1))
    reminder_obj = Mock(id=ids.goal_id, user_id=ids.second_user_id)
    mock_get_reminder_by_id.return_value = reminder_obj

    with pytest.raises(exception.ForbiddenError):
        update_reminder_service(mock_db, reminder_obj.id, ids.user_id, reminder_data)

    mock_update_reminder.assert_not_called()


@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
@patch("app.services.reminder_service.reminder_crud.update_reminder")
def test_update_reminder_service_conflict_when_new_date_in_past(
    mock_update_reminder, mock_get_reminder_by_id, mock_db, ids
):
    reminder_data = Mock(remind_at=datetime(2000, 1, 1, 10, 0, 0))
    reminder_obj = Mock(id=ids.goal_id, user_id=ids.user_id)
    mock_get_reminder_by_id.return_value = reminder_obj

    with pytest.raises(exception.ConflictError):
        update_reminder_service(mock_db, reminder_obj.id, ids.user_id, reminder_data)

    mock_update_reminder.assert_not_called()


@patch("app.services.reminder_service.reminder_crud.delete_reminder")
@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
def test_delete_reminder_service_success(
    mock_get_reminder_by_id, mock_delete_reminder, mock_db, ids
):
    reminder_obj = Mock(id=ids.goal_id, user_id=ids.user_id)
    mock_get_reminder_by_id.return_value = reminder_obj

    delete_reminder_service(mock_db, reminder_obj.id, ids.user_id)

    mock_get_reminder_by_id.assert_called_once_with(mock_db, reminder_obj.id)
    mock_delete_reminder.assert_called_once_with(mock_db, reminder_obj)


@patch("app.services.reminder_service.reminder_crud.delete_reminder")
@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
def test_delete_reminder_service_not_found(
    mock_get_reminder_by_id, mock_delete_reminder, mock_db, ids
):
    mock_get_reminder_by_id.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_reminder_service(mock_db, ids.goal_id, ids.user_id)

    mock_delete_reminder.assert_not_called()


@patch("app.services.reminder_service.reminder_crud.delete_reminder")
@patch("app.services.reminder_service.reminder_crud.get_reminder_by_id")
def test_delete_reminder_service_forbidden(
    mock_get_reminder_by_id, mock_delete_reminder, mock_db, ids
):
    reminder_obj = Mock(id=ids.goal_id, user_id=ids.second_user_id)
    mock_get_reminder_by_id.return_value = reminder_obj

    with pytest.raises(exception.ForbiddenError):
        delete_reminder_service(mock_db, reminder_obj.id, ids.user_id)

    mock_delete_reminder.assert_not_called()
