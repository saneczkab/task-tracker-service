
import fastapi
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class TeamResponse(BaseModel):
    id: int
    name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    @field_validator("email")
    def validate_email(cls, value):
        if not value:
            raise fastapi.HTTPException(status_code=400, detail="Некорректный формат email")
        return value

    nickname: str
    teams: list[TeamResponse]
    model_config = ConfigDict(from_attributes=True)
