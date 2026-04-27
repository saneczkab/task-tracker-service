from pydantic import BaseModel, ConfigDict, EmailStr


class TeamResponse(BaseModel):
    id: int
    name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    teams: list[TeamResponse]

    model_config = ConfigDict(from_attributes=True)
