from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, orm

from app.models import base


class Task(base.Base):
    __tablename__ = "Tasks"
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("Streams.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status_id = Column(Integer, nullable=True)
    priority_id = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    position = Column(Integer, nullable=False, default=0)

    assigned_users = orm.relationship("UserTask", back_populates="task")


class TaskRelation(base.Base):
    __tablename__ = "TaskRelations"

    id = Column(Integer, primary_key=True)
    task_id_1 = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    task_id_2 = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    connection_id = Column(Integer, ForeignKey("Connections.id"), nullable=False)

    task1 = orm.relationship("Task", foreign_keys=[task_id_1], backref="relations_outgoing")
    task2 = orm.relationship("Task", foreign_keys=[task_id_2], backref="relations_incoming")
    connection = orm.relationship("ConnectionType")
