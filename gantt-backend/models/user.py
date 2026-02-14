from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    user_teams = relationship("UserTeam", back_populates="user")
