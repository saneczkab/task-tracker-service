from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Status(Base):
    __tablename__ = "Statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Priority(Base):
    __tablename__ = "Priorities"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ConnectionType(Base):
    __tablename__ = "Connections"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

