from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ReminderCreate(BaseModel):
    remind_at: datetime

    @field_validator("remind_at")
    def validate_remind_at(cls, remind_at):
        if remind_at <= datetime.now():
            raise ValueError("remind_at должен быть в будущем")
        return remind_at


class ReminderUpdate(BaseModel):
    remind_at: datetime | None = None

    @field_validator("remind_at")
    def validate_remind_at(cls, remind_at):
        if remind_at and remind_at <= datetime.now():
            raise ValueError("remind_at должен быть в будущем")
        return remind_at


class ReminderResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    remind_at: datetime
    sent: bool

    model_config = ConfigDict(from_attributes=True)

