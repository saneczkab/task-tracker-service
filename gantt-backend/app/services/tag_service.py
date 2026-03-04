from sqlalchemy.orm import Session
from app.core import exception
from app.crud import tag as tag_crud
from app.services import permissions


def create_tag_service(data_base: Session, team_id: int, user_id: int, tag_data):
    """Создать новый тег"""
    permissions.check_team_access(data_base, team_id, user_id)

    return tag_crud.create_tag(data_base, team_id, tag_data.name, tag_data.color)


def get_team_tags_service(data_base: Session, team_id: int, user_id: int):
    """Получить все теги команды"""
    permissions.check_team_access(data_base, team_id, user_id)

    return tag_crud.get_team_tags(data_base, team_id)


def delete_tag_service(data_base: Session, tag_id: int, user_id: int):
    """Удалить тег"""
    tag_obj = tag_crud.get_tag_by_id(data_base, tag_id)

    if not tag_obj:
        raise exception.NotFoundError("Тег не найден")

    permissions.check_team_access(data_base, tag_obj.team_id, user_id)

    tag_crud.delete_tag(data_base, tag_obj)
