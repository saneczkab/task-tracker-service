from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/project/{proj_id}/streams")
def get_project_streams(proj_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все стримы в проекте proj_id"""
    pass


@router.post("/project/{proj_id}/stream/new")
def create_stream(proj_id: int, current_user: dict = Depends(get_current_user)):
    """Создать новый стрим в проекте proj_id"""
    pass


@router.patch("/stream/{stream_id}")
def update_stream(stream_id: int, current_user: dict = Depends(get_current_user)):
    """Частично обновить данные о стриме stream_id"""
    pass


@router.delete("/stream/{stream_id}")
def delete_stream(stream_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить стрим stream_id"""
    pass
