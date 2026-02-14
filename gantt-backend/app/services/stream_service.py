from sqlalchemy.orm import Session

from app.core import exception
from app.crud import project as project_crud
from app.crud import stream as stream_crud
from app.crud import team as team_crud
from app.models import role
from app.schemas import stream as stream_schemas


def check_project_access(data_base: Session, project_id: int, user_id: int):
    """Проверить, что пользователь имеет доступ к проекту"""
    project = project_crud.get_project_by_id(data_base, project_id)
    if not project:
        raise exception.NotFoundError("Проект не найден")

    user_team = team_crud.get_user_team_by_id(data_base, user_id, project.team_id)
    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к этой команде")

    return project, user_team


def check_stream_access(data_base: Session, stream_id: int, user_id: int):
    """Проверить доступ к стриму и получить объекты"""
    stream = stream_crud.get_stream_by_id(data_base, stream_id)
    project, user_team = check_project_access(data_base, stream.project_id, user_id)
    return stream, project, user_team


def check_admin_permission(user_team):
    """Проверить, что у пользователя права редактора"""
    if user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав редактора для этого действия")


def get_project_streams_service(data_base: Session, project_id: int, user_id: int):
    """Получить все стримы проекта"""
    check_project_access(data_base, project_id, user_id)
    streams = stream_crud.get_streams_by_project_id(data_base, project_id)
    return streams


def get_stream_service(data_base: Session, stream_id: int, user_id: int):
    """Получить информацию о стриме"""
    stream, _, _ = check_stream_access(data_base, stream_id, user_id)
    return stream


def create_stream_service(data_base: Session, project_id: int, stream_data: stream_schemas.StreamCreate, user_id: int):
    """Создать новый стрим"""
    _, user_team = check_project_access(data_base, project_id, user_id)

    check_admin_permission(user_team)

    existing = stream_crud.get_stream_by_name_and_proj_id(data_base, stream_data.name, project_id)
    if existing:
        raise exception.ConflictError("В данном проекте уже есть стрим с таким названием")

    new_stream = stream_crud.create_new_stream(data_base, project_id, stream_data)
    return new_stream


def update_stream_service(data_base: Session, stream_id: int, update_data: stream_schemas.StreamUpdate, user_id: int):
    """Обновить стрим"""
    stream, _, user_team = check_stream_access(data_base, stream_id, user_id)

    check_admin_permission(user_team)

    updated_stream = stream_crud.update_stream(data_base, stream, update_data)
    return updated_stream


def delete_stream_service(data_base: Session, stream_id: int, user_id: int):
    """Удалить стрим"""
    _, _, user_team = check_stream_access(data_base, stream_id, user_id)

    check_admin_permission(user_team)

    stream_crud.delete_stream(data_base, stream_id)
