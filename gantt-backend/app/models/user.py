from sqlalchemy import Column, Integer, String, orm
from app.models import base


class User(base.Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    user_teams = orm.relationship("UserTeam", back_populates="user")
    user_tasks = orm.relationship("UserTask", back_populates="user")
