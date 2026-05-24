from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import normalize_datetime, validate_deadline_after_start


class GoalCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = Field(None, ge=0)

    @field_validator("start_date", "deadline", mode="after")
    @classmethod
    def normalize_date_fields(cls, value: datetime | None) -> datetime | None:
        return normalize_datetime(value)

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, deadline, info):
        validate_deadline_after_start(deadline, info.data.get("start_date"))
        return deadline


class GoalUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = Field(None, ge=0)

    @field_validator("start_date", "deadline", mode="after")
    @classmethod
    def normalize_date_fields(cls, value: datetime | None) -> datetime | None:
        return normalize_datetime(value)

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, deadline, info):
        validate_deadline_after_start(deadline, info.data.get("start_date"))
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
