from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class TaskRelationCreate(BaseModel):
    task_id: int
    connection_id: int
