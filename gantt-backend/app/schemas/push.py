from pydantic import BaseModel, ConfigDict


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


class PushSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    endpoint: str
    p256dh: str
    auth: str

    model_config = ConfigDict(from_attributes=True)

