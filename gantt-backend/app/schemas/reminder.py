from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReminderCreate(BaseModel):
    remind_at: datetime


class ReminderUpdate(BaseModel):
    remind_at: datetime | None = None


class ReminderResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    remind_at: datetime
    sent: bool

    model_config = ConfigDict(from_attributes=True)

