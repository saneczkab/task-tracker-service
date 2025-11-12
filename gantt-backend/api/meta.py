from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.auth import get_current_user
from core.db import get_db
from models.meta import Status, Priority, ConnectionType
from schemas.meta import StatusResponse, PriorityResponse, ConnectionTypeResponse

router = APIRouter()


@router.get("/api/taskStatuses", response_model=List[StatusResponse], status_code=status.HTTP_200_OK)
def get_team_statuses(data_base: Session = Depends(get_db)):
    """Получить все статусы в команде team_id"""
    statuses = data_base.query(Status).all()

    return statuses


@router.get("/api/priorities", response_model=List[PriorityResponse], status_code=status.HTTP_200_OK)
def get_team_priorities(data_base: Session = Depends(get_db)):
    """Получить все приоритеты в команде team_id"""
    priorities = data_base.query(Priority).all()

    return priorities


@router.get("/api/connectionTypes", response_model=List[ConnectionTypeResponse], status_code=status.HTTP_200_OK)
def get_connection_types(data_base: Session = Depends(get_db)):
    """Получить все типы связей"""
    connections = data_base.query(ConnectionType).all()

    return connections


@router.get("/team/{team_id}/tags")
def get_team_tags(team_id: int, current_user: dict = Depends(get_current_user)):
    """Получить все теги команды team_id"""
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
