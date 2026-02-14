from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models import base


class Goal(base.Base):
    __tablename__ = "Goals"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(DateTime, nullable=False)
    stream_id = Column(Integer, ForeignKey('Streams.id'), nullable=False)

    stream = relationship("Stream", back_populates="goals")


