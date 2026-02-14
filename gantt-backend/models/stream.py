from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.user import Base


class Stream(Base):
    __tablename__ = "Streams"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("Projects.id"), nullable=False)

    project = relationship("Project", back_populates="streams")
    goals = relationship("Goal", back_populates="stream")