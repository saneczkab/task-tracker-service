from datetime import datetime
import typing
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    name: str
    description: typing.Optional[str] = None
    status_id: typing.Optional[int]
    priority_id: typing.Optional[int]
    assignee_email: typing.Optional[str] = None
    start_date: typing.Optional[datetime] = None
    deadline: typing.Optional[datetime] = None
    position: typing.Optional[int] = None


class TaskUpdate(BaseModel):
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    status_id: typing.Optional[int] = None
    priority_id: typing.Optional[int] = None
    assignee_email: typing.Optional[str] = None
    start_date: typing.Optional[datetime] = None
    deadline: typing.Optional[datetime] = None
    position: typing.Optional[int] = None


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
    description: typing.Optional[str] = None
    status_id: typing.Optional[int] = None
    priority_id: typing.Optional[int] = None
    stream_id: int
    start_date: typing.Optional[datetime] = None
    deadline: typing.Optional[datetime] = None
    assignee_email: typing.Optional[str] = None
    position: int
    relations: typing.List[TaskRelationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TaskRelationCreate(BaseModel):
    task_id: int
    connection_id: int
