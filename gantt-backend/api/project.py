from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/team/{team_id}/projects")
def get_team_projects(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все проекты в команде team_id"""
    pass


@router.post("/team/{team_id}/project/new")
def create_project(team_id: int, current_user: dict = Depends(get_current_user)):
    """Создать новый проект в команде team_id"""
    pass


@router.patch("/project/{proj_id}")
def update_project(proj_id: int, current_user: dict = Depends(get_current_user)):
    """Частично обновить данные о проекте proj_id"""
    pass


@router.delete("/project/{proj_id}")
def delete_project(proj_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить проект proj_id"""
    pass
