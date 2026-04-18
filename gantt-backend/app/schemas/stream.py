from pydantic import BaseModel, ConfigDict, Field


class StreamCreate(BaseModel):
    name: str = Field(..., min_length=1)
    position: int | None = Field(None, ge=0)


class StreamResponse(BaseModel):
    id: int
    name: str
    project_id: int
    position: int

    model_config = ConfigDict(from_attributes=True)


class StreamUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    position: int | None = Field(None, ge=0)
