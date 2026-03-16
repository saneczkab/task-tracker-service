import fastapi
from sqlalchemy import orm

from app.core import db, exception
from app.services import user_service

router = fastapi.APIRouter()


def get_current_user(request: fastapi.Request, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить текущего пользователя по токену из заголовка"""
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        raise fastapi.HTTPException(status_code=401, detail="Некорректный токен")

    try:
        return user_service.get_current_user_service(data_base, user_id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))


@router.post("/api/check-email")
def check_email(email: str, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Проверить, существует ли пользователь с данным email"""
    exists = user_service.check_email_exists_service(data_base, email)
    return {"exists": exists}


@router.post("/api/register", status_code=201)
def register(email: str, nickname: str, password: str, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Зарегистрировать нового пользователя"""
    try:
        return user_service.register_user_service(data_base, email, nickname, password)
    except exception.ConflictError as e:
        raise fastapi.HTTPException(status_code=409, detail=str(e))


@router.post("/api/login")
def login(email: str, password: str, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Авторизовать пользователя и вернуть токен"""
    try:
        return user_service.login_user_service(data_base, email, password)
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=401, detail=str(e))
