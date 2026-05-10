from datetime import datetime, timedelta

from app.crud.reminder import (
    create_reminder,
    delete_reminder,
    get_pending_reminders,
    get_reminder_by_id,
    get_reminders_by_task_and_user,
    get_reminders_by_user,
    mark_as_sent,
    update_reminder,
)
from app.models import task as task_model
from app.schemas.reminder import ReminderUpdate


def test_get_reminder_by_id_returns_reminder(db_session, reminder_obj):
    result = get_reminder_by_id(db_session, reminder_obj.id)

    assert result.id == reminder_obj.id
    assert result.task_id == reminder_obj.task_id
    assert result.user_id == reminder_obj.user_id


def test_get_reminder_by_id_returns_none_when_not_found(db_session):
    result = get_reminder_by_id(db_session, 999)

    assert result is None


def test_get_reminders_by_task_and_user_returns_list(
    db_session, reminder_obj, second_user_obj
):
    same_task_other_user = task_model.TaskReminder(
        id=44,
        task_id=reminder_obj.task_id,
        user_id=second_user_obj.id,
        remind_at=reminder_obj.remind_at,
        sent=True,
    )
    db_session.add(same_task_other_user)
    db_session.commit()

    result = get_reminders_by_task_and_user(
        db_session, reminder_obj.task_id, reminder_obj.user_id
    )

    assert len(result) == 1
    assert result[0].id == reminder_obj.id


def test_get_reminders_by_task_and_user_returns_empty_list_when_not_found(db_session):
    result = get_reminders_by_task_and_user(db_session, 999, 999)

    assert result == []


def test_get_reminders_by_user_returns_list(
    db_session, reminder_obj, second_reminder_obj
):
    result = get_reminders_by_user(db_session, reminder_obj.user_id)

    assert len(result) == 2
    assert {item.id for item in result} == {reminder_obj.id, second_reminder_obj.id}


def test_get_reminders_by_user_returns_empty_list_when_not_found(db_session):
    result = get_reminders_by_user(db_session, 999)

    assert result == []


def test_get_pending_reminders_returns_only_unsent(
    db_session, reminder_obj, second_reminder_obj
):
    result = get_pending_reminders(db_session)

    assert len(result) == 1
    assert result[0].id == reminder_obj.id
    assert all(item.sent is False for item in result)


def test_create_reminder_persists_reminder(db_session, task_obj, user_obj):
    remind_at = datetime.now() + timedelta(days=5)

    result = create_reminder(db_session, task_obj.id, user_obj.id, remind_at)
    db_session.commit()
    db_session.refresh(result)

    assert result.id is not None
    assert result.task_id == task_obj.id
    assert result.user_id == user_obj.id
    assert result.remind_at == remind_at
    assert result.sent is False


def test_update_reminder_updates_fields(db_session, reminder_obj):
    new_remind_at = datetime.now() + timedelta(days=10)
    update_data = ReminderUpdate(remind_at=new_remind_at)

    result = update_reminder(db_session, reminder_obj, update_data)

    assert reminder_obj.remind_at == new_remind_at
    assert result is reminder_obj


def test_update_reminder_empty_data(db_session, reminder_obj):
    update_data = ReminderUpdate()

    result = update_reminder(db_session, reminder_obj, update_data)

    assert result is reminder_obj


def test_mark_as_sent_sets_flag(db_session, reminder_obj):
    result = mark_as_sent(db_session, reminder_obj)

    assert result.sent is True
    assert get_pending_reminders(db_session) == []


def test_delete_reminder_removes_record(db_session, reminder_obj):
    delete_reminder(db_session, reminder_obj)

    assert get_reminder_by_id(db_session, reminder_obj.id) is None
    assert get_reminders_by_user(db_session, reminder_obj.user_id) == []
