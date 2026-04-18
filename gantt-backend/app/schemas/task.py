from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.tag import TagResponse
from app.schemas.custom_field import TaskCustomFieldValue, TaskCustomFieldValueBase


class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    status_id: int | None = Field(None, gt=0)
    priority_id: int | None = Field(None, gt=0)
    assignee_email: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = Field(None, ge=0)
    tag_ids: list[int] | None = None
    custom_fields: list[TaskCustomFieldValueBase] | None = None

    @field_validator("deadline")
    def validate_deadline(cls, deadline, info):
        start_date = info.data.get("start_date")
        if start_date and deadline and deadline <= start_date:
            raise ValueError("deadline должен быть больше start_date")
        return deadline


class TaskUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    status_id: int | None = Field(None, gt=0)
    priority_id: int | None = Field(None, gt=0)
    assignee_email: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = Field(None, ge=0)
    tag_ids: list[int] | None = None
    custom_fields: list[TaskCustomFieldValueBase] | None = None

    @field_validator("deadline")
    def validate_deadline(cls, deadline, info):
        start_date = info.data.get("start_date")
        if start_date and deadline and deadline <= start_date:
            raise ValueError("deadline должен быть больше start_date")
        return deadline


class TaskRelationResponse(BaseModel):
    id: int
    task_id_1: int
    task_id_2: int
    connection_id: int
    connection_name: str

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    status_id: int | None = None
    priority_id: int | None = None
    stream_id: int
    start_date: datetime | None = None
    deadline: datetime | None = None
    assignee_email: str | None = None
    position: int
    relations: list[TaskRelationResponse] = []
    tags: list[TagResponse] = Field(default_factory=list, alias="tag_list")
    custom_field_values: list[TaskCustomFieldValue] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TaskResponseFull(BaseModel):
    id: int
    name: str
    description: str | None = None
    status_id: int | None = None
    priority_id: int | None = None
    stream_id: int
    start_date: datetime | None = None
    deadline: datetime | None = None
    assignee_email: str | None = None
    position: int
    relations: list[TaskRelationResponse] = []
    team_id: int | None = None
    team_name: str | None = None
    project_name: str | None = None
    stream_name: str | None = None
    tags: list[TagResponse] = Field(default_factory=list, alias="tag_list")
    custom_field_values: list[TaskCustomFieldValue] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TaskRelationCreate(BaseModel):
    task_id: int
    connection_id: int


class TaskHistoryEntry(BaseModel):
    id: int
    task_id: int
    changed_by_id: int
    changed_by_email: str | None = None
    changed_at: datetime
    field_name: str
    old_value: str | None = None
    new_value: str | None = None

    model_config = ConfigDict(from_attributes=True)

