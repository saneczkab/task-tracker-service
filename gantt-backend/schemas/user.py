from typing import List

from pydantic import BaseModel, EmailStr


class TeamResponse(BaseModel):
    id: int
    name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    teams: List[TeamResponse]
    class Config:
        from_attributes = True

