from pydantic import BaseModel, ConfigDict


class StreamCreate(BaseModel):
    name: str
    position: int | None = None


class StreamResponse(BaseModel):
    id: int
    name: str
    project_id: int
    position: int

    model_config = ConfigDict(from_attributes=True)


class StreamUpdate(BaseModel):
    name: str | None = None
    position: int | None = None
