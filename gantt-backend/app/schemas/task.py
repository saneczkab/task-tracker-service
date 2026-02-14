from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status_id: Optional[int]
    priority_id: Optional[int]
    assignee_email: Optional[str] = None  # TODO: multiple user responsible
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    assignee_email: Optional[str] = None  # TODO: multiple user responsible
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    stream_id: int
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    assignee_email: Optional[str] = None
    # TODO: multiple user responsible

    model_config = ConfigDict(from_attributes=True)
