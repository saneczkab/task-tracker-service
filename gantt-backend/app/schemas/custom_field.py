from datetime import date, datetime
from typing import Optional

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
    value_string: Optional[str] = None
    value_text: Optional[str] = None
    value_date: Optional[date] = None
    value_datetime: Optional[datetime] = None
    value_bool: Optional[bool] = None



class TaskCustomFieldValueUpdate(BaseModel):
    value_string: Optional[str] = None
    value_text: Optional[str] = None
    value_date: Optional[date] = None
    value_datetime: Optional[datetime] = None
    value_bool: Optional[bool] = None


class TaskCustomFieldValue(TaskCustomFieldValueBase):
    id: int
    task_id: int

    model_config = ConfigDict(from_attributes=True)
