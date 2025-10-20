from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/user/{user_id}")
def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Получить всю инфу о пользователе(никнейм, почта, команды)"""
    pass


@router.post("/user/new")
def create_user():
    """Зарегистрировать пользователя"""
    pass


@router.patch("/user/{user_id}")
def update_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Частично обновить данные о пользователе user_id"""
    pass


@router.delete("/user/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить юзер user_id"""
    pass
