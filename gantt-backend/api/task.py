from email.header import Header
from typing import Optional

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/project/{proj_id}/tasks")
def get_project_tasks(proj_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все задачи в проекте proj_id"""
    pass


@router.get("/stream/{stream_id}/tasks")
def get_stream_tasks(stream_id: int, filter: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Получить все задачи в стриме stream_id"""
    pass


@router.post("/stream/{stream_id}/task/new")
def create_task(stream_id: int, current_user: dict = Depends(get_current_user)):
    """Создать задачу в стриме stream_id"""
    pass


@router.patch("/task/{task_id}")
def update_task(task_id: int, current_user: dict = Depends(get_current_user)):
    """Частично обновить данные о задаче task_id"""
    pass


@router.delete("/task/{task_id}")
def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить задачу task_id"""
    pass
