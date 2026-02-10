from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import base


class Status(base.Base):
    __tablename__ = "Status"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Priority(base.Base):
    __tablename__ = "Priority"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ConnectionType(base.Base):
    __tablename__ = "Connections"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class UserTask(base.Base):
    __tablename__ = "UserTask"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("Tasks.id"), nullable=False)

    user = relationship("User", back_populates="assigned_tasks")
    task = relationship("Task", back_populates="assigned_users")
