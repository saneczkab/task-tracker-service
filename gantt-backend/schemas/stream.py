from typing import Optional

from pydantic import BaseModel


class StreamCreate(BaseModel):
    name: str


class StreamResponse(BaseModel):
    id: int
    name: str
    project_id: int

    class Config:
        from_attributes = True


class StreamUpdate(BaseModel):
    name: Optional[str] = None