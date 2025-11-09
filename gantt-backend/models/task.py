from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Task(Base):
    __tablename__ = "Tasks"
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("Streams.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    status_id = Column(Integer, nullable=False)
    priority_id = Column(Integer, nullable=False)

    # TODO: fix
    # stream = relationship("Stream", back_populates="tasks")
