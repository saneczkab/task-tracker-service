from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1)
    color: str


class TagResponse(BaseModel):
    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)
