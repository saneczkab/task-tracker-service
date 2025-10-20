from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/stream/{stream_id}/goals")
def get_stream_goals(stream_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все цели у стрима stream_id"""
    pass


@router.post("/stream/{stream_id}/goal/new")
def create_goal(stream_id: int, current_user: dict = Depends(get_current_user)):
    """Создать цель в стриме stream_id"""
    pass


@router.patch("/goal/{goal_id}")
def update_goal(goal_id: int, current_user: dict = Depends(get_current_user)):
    """Частично обновить данные о цели goal_id"""
    pass


@router.delete("/goal/{goal_id}")
def delete_goal(goal_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить цель goal_id"""
    pass
