from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    user_teams = relationship("UserTeam", back_populates="user")
