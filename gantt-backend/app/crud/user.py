from sqlalchemy import exc, orm

from app.core import exception
from app.models import user


def get_user_by_id(data_base: orm.Session, user_id: int):
    u = data_base.query(user.User).filter(user.User.id == user_id).first()
    if not u:
        raise exception.NotFoundError("Пользователь не найден")
    return u


def get_user_by_email(data_base: orm.Session, email: str):
    return data_base.query(user.User).filter(user.User.email == email).first()

def get_user_by_nickname(data_base: orm.Session, nickname: str):
    return (
        data_base
        .query(user.User)
        .filter(user.User.nickname == nickname)
        .first()
    )


def create_user(data_base: orm.Session, email: str, nickname: str, password_hash: str):
    new_user = user.User(
        email=email,
        nickname=nickname,
        password_hash=password_hash
    )

    data_base.add(new_user)

    try:
        data_base.commit()
        data_base.refresh(new_user)
    except exc.IntegrityError:
        data_base.rollback()
        raise exception.ConflictError("Нарушено ограничение уникальности")

    return new_user