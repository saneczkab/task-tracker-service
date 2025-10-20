from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.post("/register")
def register():
    """Создать нового юзера"""
    pass


@router.post("/login")
def login():
    """Авторизация"""
    pass
