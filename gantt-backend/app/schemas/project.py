
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)


class ProjectResponse(BaseModel):
    id: int
    name: str
    team_id: int

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
