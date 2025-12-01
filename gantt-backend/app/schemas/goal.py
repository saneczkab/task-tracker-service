import typing
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    name: str
    description: typing.Optional[str] = None
    deadline: typing.Optional[datetime] = None
    position: typing.Optional[int] = None


class GoalUpdate(BaseModel):
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    deadline: typing.Optional[datetime] = None
    position: typing.Optional[int] = None


class GoalResponse(BaseModel):
    id: int
    name: str
    description: typing.Optional[str] = None
    deadline: typing.Optional[datetime] = None
    stream_id: int
    position: int

    model_config = ConfigDict(from_attributes=True)
