from fastapi import APIRouter, status, Header, HTTPException, Depends
from jose import JWTError
from sqlalchemy.orm import Session

from core import security
from core.db import get_db
from models.user import User

router = APIRouter()


async def get_current_user(authorization: str = Header(...), data_base: Session = Depends(get_db)):
    """Получение текущего пользователя из токена"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")

    token = authorization.split(" ")[1]

    try:
        payload = security.decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный или просроченный токен")

    user_id = int(payload.get("sub"))
    user = data_base.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return user


@router.post("/api/check-email")
def check_email(email: str, data_base: Session = Depends(get_db)):
    """Проверить существует ли email в базе данных"""
    user = data_base.query(User).filter(User.email == email).first()
    return {
        "exists": user is not None
    }


@router.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(email: str, nickname: str, password: str, data_base: Session = Depends(get_db)):
    """Регистрация"""
    if data_base.query(User).filter(User.nickname == nickname).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Данное имя пользователя уже занято")

    user = User(email=email, nickname=nickname, password_hash=security.get_password_hash(password))

    data_base.add(user)
    data_base.commit()
    data_base.refresh(user)

    token = security.create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "Bearer"}


@router.post("/api/login", status_code=status.HTTP_201_CREATED)
def login(email: str, password: str, data_base: Session = Depends(get_db)):
    """Авторизация"""
    user = data_base.query(User).filter(User.email == email).first()

    if not user or not security.verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные для входа")

    token = security.create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
