from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, orm

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

    @property
    def relations(self):
        return (self.relations_outgoing or []) + (self.relations_incoming or [])


class TaskRelation(base.Base):
    __tablename__ = "TaskRelations"

    id = Column(Integer, primary_key=True)
    task_id_1 = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    task_id_2 = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    connection_id = Column(Integer, ForeignKey("Connections.id"), nullable=False)

    task1 = orm.relationship("Task", foreign_keys=[task_id_1], backref="relations_outgoing")
    task2 = orm.relationship("Task", foreign_keys=[task_id_2], backref="relations_incoming")
    connection = orm.relationship("ConnectionType")

    @property
    def connection_name(self):
        return self.connection.name if self.connection else None


class TaskReminder(base.Base):
    __tablename__ = "task_reminders"

    id = Column(Integer, primary_key=True)

    task_id = Column(Integer, ForeignKey("Tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)

    remind_at = Column(DateTime, nullable=False)
    sent = Column(Boolean, default=False)