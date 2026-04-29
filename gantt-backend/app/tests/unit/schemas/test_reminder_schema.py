from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.reminder import ReminderCreate, ReminderUpdate


def test_reminder_create_future_datetime():
    future = datetime.now() + timedelta(days=1)
    result = ReminderCreate(remind_at=future)
    assert result.remind_at == future


def test_reminder_create_past_datetime():
    past = datetime.now() - timedelta(days=1)
    with pytest.raises(ValidationError):
        ReminderCreate(remind_at=past)


def test_reminder_create_now_datetime():
    now = datetime.now()
    with pytest.raises(ValidationError):
        ReminderCreate(remind_at=now)


def test_reminder_update_empty_payload():
    result = ReminderUpdate()
    assert result.remind_at is None


def test_reminder_update_future_datetime():
    future = datetime.now() + timedelta(days=1)
    result = ReminderUpdate(remind_at=future)
    assert result.remind_at == future


def test_reminder_update_past_datetime():
    past = datetime.now() - timedelta(days=1)
    with pytest.raises(ValidationError):
        ReminderUpdate(remind_at=past)
