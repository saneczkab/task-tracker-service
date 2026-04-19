from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GoalCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = Field(None, ge=0)

    @field_validator("deadline")
    def validate_deadline(cls, deadline, info):
        start_date = info.data.get("start_date")
        if start_date and deadline and deadline <= start_date:
            raise ValueError("deadline должен быть больше start_date")
        return deadline


class GoalUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = Field(None, ge=0)

    @field_validator("deadline")
    def validate_deadline(cls, deadline, info):
        start_date = info.data.get("start_date")
        if start_date and deadline and deadline <= start_date:
            raise ValueError("deadline должен быть больше start_date")
        return deadline


class GoalResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    stream_id: int
    position: int

    model_config = ConfigDict(from_attributes=True)
