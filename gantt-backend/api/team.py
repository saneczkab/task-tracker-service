from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/team/{team_id}/users")
def get_team_users(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить всех пользователей в команде team_id"""
    pass


@router.post("/user/{user_id}/team/new")
def create_team(user_id: int, current_user: dict = Depends(get_current_user)):
    """Создание новой команды пользователем user_id"""
    pass


@router.patch("/team/{team_id}")
def update_team(team_id: int, current_user: dict = Depends(get_current_user)):
    """Частично обновить данные о команде team_id"""
    pass


@router.delete("/team/{team_id}")
def delete_team(team_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить команду team_id"""
    pass
