from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict


class TeamResponse(BaseModel):
    id: int
    name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    teams: List[TeamResponse]
    model_config = ConfigDict(from_attributes=True)
