from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models import base
import datetime

class RequestLimit(base.Base):
    __tablename__ = "RequestLimit"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    target_date = Column(Date, default=datetime.date.today, nullable=False)
    request_count = Column(Integer, default=0, nullable=False)

    user = relationship("User")