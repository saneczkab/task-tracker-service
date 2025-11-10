from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status_id: int
    priority_id: int


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None


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

    class Config:
        from_attributes = True
