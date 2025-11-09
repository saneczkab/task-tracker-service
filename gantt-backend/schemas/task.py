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
    description: str
    status_id: int
    priority_id: int
    stream_id: int

    class Config:
        from_attributes = True
