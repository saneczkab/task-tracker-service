from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, Date, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.models import base
import enum


class CustomFieldType(str, enum.Enum):
    STRING = "string"
    TEXT = "text"
    DATE = "date"
    DATETIME = "datetime"
    BOOL = "bool"


class CustomField(base.Base):
    __tablename__ = "custom_fields"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("Teams.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(CustomFieldType), nullable=False)

    team = relationship("Team", back_populates="custom_fields")
    values = relationship("TaskCustomFieldValue", back_populates="custom_field", cascade="all, delete-orphan")


class TaskCustomFieldValue(base.Base):
    __tablename__ = "task_custom_field_values"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    custom_field_id = Column(Integer, ForeignKey("custom_fields.id"), nullable=False)

    value_string = Column(String(255), nullable=True)
    value_text = Column(Text, nullable=True)
    value_date = Column(Date, nullable=True)
    value_datetime = Column(DateTime, nullable=True)
    value_bool = Column(Boolean, nullable=True)

    task = relationship("Task", back_populates="custom_field_values")
    custom_field = relationship("CustomField", back_populates="values")

