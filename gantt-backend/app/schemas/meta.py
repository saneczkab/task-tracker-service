from pydantic import BaseModel


class StatusResponse(BaseModel):
    id: int
    name: str


class PriorityResponse(BaseModel):
    id: int
    name: str


class ConnectionTypeResponse(BaseModel):
    id: int
    name: str
