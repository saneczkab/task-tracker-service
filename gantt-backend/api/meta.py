from email.header import Header

from fastapi import APIRouter, Depends

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    """Получение текущего пользователя из токена"""
    pass


@router.get("/team/{team_id}/taskStatuses")
def get_team_statuses(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все статусы в команде team_id"""
    pass


@router.get("/team/{team_id}/priorities")
def get_team_priorities(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все приоритеты в команде team_id"""
    pass


@router.get("/team/{team_id}/tags")
def get_team_tags(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все теги команды team_id"""
    pass


@router.get("/connectionTypes")
def get_connection_types():
    """Получить все типы связей"""
    pass


@router.get("/reminderTypes")
def get_reminder_types():
    """Получить все типы напоминалок"""
    pass


@router.get("/fieldTypes")
def get_field_types():
    """Получить все типы поля"""
    pass


@router.get("/team/{team_id}/fields")
def get_team_fields(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все поля у задач в команде team_id"""
    pass


@router.post("/team/{team_id}/fields/new")
def create_field(team_id: int, current_user: dict = Depends(get_current_user)):
    """Добавить новое поле для задач в команде team_id"""
    pass


@router.get("/user/{user_id}/team/{team_id}/role")
def get_user_role(user_id: int, team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить роль юзера user_id в команде team_id"""
    pass


@router.post("/team/{team_id}/statuses/new")
def create_status(team_id: int, current_user: dict = Depends(get_current_user)):
    """Создать новый статус в команде team_id"""
    pass


@router.post("/team/{team_id}/priorities/new")
def create_priority(team_id: int, current_user: dict = Depends(get_current_user)):
    """Создать новый приоритет в команде team_id"""
    pass


@router.post("/team/{team_id}/tags/new")
def create_tag(team_id: int, current_user: dict = Depends(get_current_user)):
    """Создать новый тэг в команде team_id"""
    pass


@router.delete("/status/{status_id}")
def delete_status(status_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить статус status_id"""
    pass


@router.delete("/priorities/{priority_id}")
def delete_priority(priority_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить приоритет priority_id"""
    pass


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить тэг tag_id"""
    pass


@router.delete("/fields/{field_id}")
def delete_field(field_id: int, current_user: dict = Depends(get_current_user)):
    """Удалить поле field_id"""
    pass
