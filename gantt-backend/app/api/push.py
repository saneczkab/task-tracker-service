import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.schemas import push as push_schemas
from app.services import push_service

router = fastapi.APIRouter(prefix="/api/push", tags=["Push Notifications"])


@router.post("/subscribe", response_model=push_schemas.PushSubscriptionResponse)
def subscribe_to_push(
    subscription_data: push_schemas.PushSubscriptionCreate,
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Подписаться на push уведомления"""
    subscription = push_service.create_push_subscription_service(
        data_base,
        user_id=current_user.id,
        endpoint=subscription_data.endpoint,
        p256dh=subscription_data.p256dh,
        auth=subscription_data.auth
    )
    return subscription


@router.get("/subscriptions", response_model=list[push_schemas.PushSubscriptionResponse])
def get_subscriptions(
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Получить все подписки пользователя"""
    return push_service.get_user_subscriptions_service(data_base, current_user.id)


@router.delete("/subscriptions/{subscription_id}", status_code=204)
def delete_subscription(
    subscription_id: int,
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Удалить подписку"""
    try:
        push_service.delete_push_subscription_service(
            data_base,
            subscription_id,
            current_user.id
        )
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))

