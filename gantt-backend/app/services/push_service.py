import json

from pywebpush import webpush
from sqlalchemy import orm

from app.core import exception
from app.core.config import settings
from app.core.db import SessionLocal
from app.crud import push as push_crud
from app.crud import reminder as reminder_crud


def send_push(reminder_id: int):
    """Отправить push уведомление по напоминанию"""
    db = SessionLocal()

    reminder = reminder_crud.get_reminder_by_id(db, reminder_id)

    if not reminder or reminder.sent:
        db.close()
        return

    subscriptions = push_crud.get_subscriptions_by_user(db, reminder.user_id)

    payload = json.dumps({"title": "Напоминание","body": f"Приближается дедлайн по задаче {reminder.task_id}"})

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    }
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_CLAIMS_SUB}
            )
        except Exception:
            pass

    reminder_crud.mark_as_sent(db, reminder)
    db.close()


def create_push_subscription_service(
    data_base: orm.Session,
    user_id: int,
    endpoint: str,
    p256dh: str,
    auth: str
):
    """Создать подписку на push уведомления"""
    subscription = push_crud.create_subscription(
        data_base,
        user_id=user_id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth
    )
    data_base.commit()
    data_base.refresh(subscription)
    return subscription


def get_user_subscriptions_service(data_base: orm.Session, user_id: int):
    """Получить все подписки пользователя"""
    return push_crud.get_subscriptions_by_user(data_base, user_id)


def delete_push_subscription_service(data_base: orm.Session, subscription_id: int, user_id: int):
    """Удалить подписку на push уведомления"""
    subscription = push_crud.get_subscription_by_id(data_base, subscription_id)
    if not subscription:
        raise exception.NotFoundError("Подписка не найдена")

    if subscription.user_id != user_id:
        raise exception.ForbiddenError("Вы не можете удалить чужую подписку")

    push_crud.delete_subscription(data_base, subscription)
