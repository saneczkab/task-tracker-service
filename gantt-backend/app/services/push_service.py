import json

from pywebpush import webpush
from sqlalchemy import orm

from app.core import exception
from app.core.config import settings
from app.core.db import SessionLocal
from app.crud import push as push_crud
from app.crud import reminder as reminder_crud
from app.crud import task as task_crud
from app.crud import stream as stream_crud
from app.crud import project as project_crud
from app.crud import team as team_crud


def send_push(reminder_id: int):
    """Отправить push уведомление по напоминанию"""
    db = SessionLocal()

    reminder = reminder_crud.get_reminder_by_id(db, reminder_id)

    if not reminder or reminder.sent:
        db.close()
        return

    subscriptions = push_crud.get_subscriptions_by_user(db, reminder.user_id)
    task_id = reminder.task_id
    task = task_crud.get_task_by_id(db, task_id)
    stream = stream_crud.get_stream_by_id(db, task.stream_id) if task else None
    project = project_crud.get_project_by_id(db, stream.project_id) if stream else None
    team = team_crud.get_team_by_id(db, project.team_id) if project else None
    if not task or not stream or not project or not team:
        db.close()
        return

    payload = json.dumps(
        {
            "title": "Напоминание",
            "body": f"Приближается дедлайн по задаче {task.name}",
            "stream_id": stream.id,
            "team_id": team.id,
        }
    )

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    },
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_CLAIMS_SUB},
            )
        except Exception:
            pass

    reminder_crud.mark_as_sent(db, reminder)
    db.close()


def create_push_subscription_service(
    data_base: orm.Session, user_id: int, endpoint: str, p256dh: str, auth: str
):
    """Создать подписку на push уведомления"""
    subscription = push_crud.create_subscription(
        data_base, user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth
    )
    data_base.commit()
    data_base.refresh(subscription)
    return subscription


def get_user_subscriptions_service(data_base: orm.Session, user_id: int):
    """Получить все подписки пользователя"""
    return push_crud.get_subscriptions_by_user(data_base, user_id)


def delete_push_subscription_service(
    data_base: orm.Session, subscription_id: int, user_id: int
):
    """Удалить подписку на push уведомления"""
    subscription = push_crud.get_subscription_by_id(data_base, subscription_id)
    if not subscription:
        raise exception.NotFoundError("Подписка не найдена")

    if subscription.user_id != user_id:
        raise exception.ForbiddenError("Вы не можете удалить чужую подписку")

    push_crud.delete_subscription(data_base, subscription)
