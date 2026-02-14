from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class GoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: datetime


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class GoalResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    deadline: datetime
    stream_id: int

    class Config:
        from_attributes = True
