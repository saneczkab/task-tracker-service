from typing import Optional
from pydantic import BaseModel, ConfigDict


class StreamCreate(BaseModel):
    name: str


class StreamResponse(BaseModel):
    id: int
    name: str
    project_id: int

    model_config = ConfigDict(from_attributes=True)


class StreamUpdate(BaseModel):
    name: Optional[str] = None
