from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagResponse


class TaskCreate(BaseModel):
    name: str
    description: str | None = None
    status_id: int | None
    priority_id: int | None
    assignee_email: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = None


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status_id: int | None = None
    priority_id: int | None = None
    assignee_email: str | None = None
    start_date: datetime | None = None
    deadline: datetime | None = None
    position: int | None = None
    tag_ids: list[int] | None = None


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

