import typing

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    team_id: int

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: typing.Optional[str] = None
