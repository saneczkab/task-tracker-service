from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import base


class Team(base.Base):
    __tablename__ = "Teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    user_teams = relationship("UserTeam", back_populates="team")
    projects = relationship("Project", back_populates="team")


class UserTeam(base.Base):
    __tablename__ = "UserTeam"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    team_id = Column(Integer, ForeignKey("Teams.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("Roles.id"), nullable=False)

    user = relationship("User", back_populates="user_teams")
    team = relationship("Team", back_populates="user_teams")
    role = relationship("Role")


class Role(base.Base):
    __tablename__ = "Roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
