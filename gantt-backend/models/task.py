from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Task(Base):
    __tablename__ = "Tasks"
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("Streams.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    status_id = Column(Integer, nullable=False)
    priority_id = Column(Integer, nullable=False)

    stream = relationship("Stream", back_populates="tasks")
