from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.custom_field import CustomFieldType


class CustomFieldBase(BaseModel):
    name: str = Field(..., min_length=1)
    type: CustomFieldType


class CustomField(CustomFieldBase):
    id: int
    team_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskCustomFieldValueBase(BaseModel):
    custom_field_id: int = Field(..., gt=0)
    value_string: str | None = None
    value_text: str | None = None
    value_date: date | None = None
    value_datetime: datetime | None = None
    value_bool: bool | None = None


class TaskCustomFieldValueUpdate(BaseModel):
    value_string: str | None = None
    value_text: str | None = None
    value_date: date | None = None
    value_datetime: datetime | None = None
    value_bool: bool | None = None


class TaskCustomFieldValue(TaskCustomFieldValueBase):
    id: int
    task_id: int

    model_config = ConfigDict(from_attributes=True)
