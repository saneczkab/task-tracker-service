from sqlalchemy import Column, Integer, String, ForeignKey
from app.models import base


class PushSubscription(base.Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)

    endpoint = Column(String, nullable=False)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)