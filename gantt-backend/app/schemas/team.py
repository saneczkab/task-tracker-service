from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRole(str, Enum):
    READER = "Reader"
    EDITOR = "Editor"


class UserWithRoleResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    newUsers: Optional[List[EmailStr]] = None
    deleteUsers: Optional[List[EmailStr]] = None
