from sqlalchemy import orm
from app.crud import user as user_crud
from app.crud import team as team_crud

from app.core import security, exception


def get_current_user_service(data_base: orm.Session, user_id: int):
    return user_crud.get_user_by_id(data_base, user_id)


def check_email_exists_service(data_base: orm.Session, email: str):
    u = user_crud.get_user_by_email(data_base, email)
    return u is not None


def register_user_service(data_base: orm.Session, email: str, nickname: str, password: str):
    hashed_pass = security.get_password_hash(password)

    new_user = user_crud.create_user(data_base=data_base, email=email, nickname=nickname, password_hash=hashed_pass)

    token = security.create_access_token({"sub": str(new_user.id)})
    return {"access_token": token, "token_type": "Bearer"}


def login_user_service(data_base: orm.Session, email: str, password: str):
    u = user_crud.get_user_by_email(data_base, email)
    if not u or not security.verify_password(password, u.password_hash):
        raise exception.ForbiddenError("Неверные данные для входа")

    token = security.create_access_token({"sub": str(u.id)})
    return {"access_token": token, "token_type": "Bearer"}


def get_user_by_token_service(data_base: orm.Session, current_user_id: int):
    user_obj = user_crud.get_user_by_id(data_base, current_user_id)
    teams = team_crud.get_teams_by_user(data_base, user_obj.id)
    return user_obj, teams


def get_user_service(data_base: orm.Session, requested_user_id: int, current_user_id: int):
    if requested_user_id != current_user_id:
        raise exception.ForbiddenError("Вы можете получить только свои данные")

    user_obj = user_crud.get_user_by_id(data_base, requested_user_id)
    teams = team_crud.get_teams_by_user(data_base, requested_user_id)
    return user_obj, teams