import datetime

from jose import jwt, exceptions
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля и его хеша"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создание JWT токена доступа (short-lived)"""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encode_jwt


def create_refresh_token(data: dict) -> str:
    """Создание JWT токена для обновления (long-lived)"""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encode_jwt


def decode_access_token(token: str) -> dict:
    """Проверка и декодирование токена"""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload


def refresh_access_token(refresh_token: str) -> str:
    """Обновление access токена с использованием refresh токена"""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_data = {k: v for k, v in payload.items() if k not in ["exp", "type", "iat"]}
        return create_access_token(user_data)
    except exceptions.ExpiredSignatureError:
        raise ValueError("Refresh token expired")
    except exceptions.JWTError as e:
        raise ValueError(f"Invalid refresh token: {str(e)}")
