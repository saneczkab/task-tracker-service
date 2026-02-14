import fastapi
from sqlalchemy import orm, exc

from app.core import db, security
from app.models import user

router = fastapi.APIRouter()


def get_current_user(request: fastapi.Request, data_base: orm.Session = fastapi.Depends(db.get_db)):
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")

    u = data_base.query(user.User).filter(user.User.id == user_id).first()

    if not u:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return u


@router.post("/api/check-email")
def check_email(email: str, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Проверить существует ли email в базе данных"""
    u = data_base.query(user.User).filter(user.User.email == email).first()
    return {"exists": u is not None}


@router.post("/api/register", status_code=fastapi.status.HTTP_201_CREATED)
def register(email: str, nickname: str, password: str, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Регистрация"""
    u = user.User(
        email=email,
        nickname=nickname,
        password_hash=security.get_password_hash(password)
    )

    data_base.add(u)
    try:
        data_base.commit()
        data_base.refresh(u)
    except exc.IntegrityError:
        data_base.rollback()
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                    detail="Пользователь с таким email или именем уже существует")

    token = security.create_access_token({"sub": str(u.id)})

    return {"access_token": token, "token_type": "Bearer"}


@router.post("/api/login")
def login(email: str, password: str, data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Авторизация"""
    u = data_base.query(user.User).filter(user.User.email == email).first()

    if not u or not security.verify_password(password, u.password_hash):
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                                    detail="Неверные данные для входа")

    token = security.create_access_token({"sub": str(u.id)})

    return {"access_token": token, "token_type": "Bearer"}