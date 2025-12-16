from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import base


class Project(base.Base):
    __tablename__ = "Projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey('Teams.id'), nullable=False)

    team = relationship("Team", back_populates="projects")
    streams = relationship("Stream", back_populates="project")
