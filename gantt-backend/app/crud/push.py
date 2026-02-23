from sqlalchemy import orm

from app.models import push


def get_subscription_by_id(db: orm.Session, subscription_id: int):
    """Получить подписку по id"""
    return db.query(push.PushSubscription).filter(push.PushSubscription.id == subscription_id).first()


def get_subscriptions_by_user(db: orm.Session, user_id: int):
    """Получить все подписки пользователя"""
    return db.query(push.PushSubscription).filter(
        push.PushSubscription.user_id == user_id
    ).all()


def create_subscription(db: orm.Session, user_id: int, endpoint: str, p256dh: str, auth: str):
    """Создать подписку на push уведомления"""
    subscription = push.PushSubscription(
        user_id=user_id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth
    )
    db.add(subscription)
    db.flush()
    return subscription


def delete_subscription(db: orm.Session, subscription_obj):
    """Удалить подписку на push уведомления"""
    db.delete(subscription_obj)
    db.commit()

