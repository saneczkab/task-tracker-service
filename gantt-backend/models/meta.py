from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Status(Base):
    __tablename__ = "Status"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Priority(Base):
    __tablename__ = "Priority"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ConnectionType(Base):
    __tablename__ = "Connections"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class UserTask(Base):
    __tablename__ = "UserTask"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("Tasks.id"), nullable=False)

    user = relationship("User", backref="user_tasks")
    task = relationship("Task", backref="user_tasks")

