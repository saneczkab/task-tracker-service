from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    name: str = Field(..., min_length=1)


class TeamResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class TeamUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    newUsers: list[EmailStr] | None = None
    deleteUsers: list[EmailStr] | None = None
