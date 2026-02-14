from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from models.base import Base


class Task(Base):
    __tablename__ = "Tasks"
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("Streams.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status_id = Column(Integer, nullable=True)
    priority_id = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)

    # TODO: fix
    # stream = relationship("Stream", back_populates="tasks")
