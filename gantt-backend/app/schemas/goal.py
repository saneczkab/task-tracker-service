from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = None


class GoalUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = None


class GoalResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    stream_id: int
    position: int

    model_config = ConfigDict(from_attributes=True)
