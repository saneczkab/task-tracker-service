from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str
    color: str


class TagResponse(BaseModel):
    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)
