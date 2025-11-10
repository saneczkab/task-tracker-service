from sqlalchemy import Column, Integer, String
from models.base import Base


class Status(Base):
    __tablename__ = "Status"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Priority(Base):
    __tablename__ = "Priority"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ConnectionType(Base):
    __tablename__ = "Connections"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

