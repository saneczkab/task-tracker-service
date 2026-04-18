from sqlalchemy.orm import Session

from app.core import exception
from app.crud import stream as stream_crud
from app.models import stream as stream_model
from app.schemas import stream as stream_schemas
from app.services import permissions


def get_project_streams_service(data_base: Session, project_id: int, user_id: int):
    """Получить все стримы проекта"""
    permissions.check_project_access(data_base, project_id, user_id)
    streams = stream_crud.get_streams_by_project_id(data_base, project_id)
    return streams


def get_stream_service(data_base: Session, stream_id: int, user_id: int):
    """Получить информацию о стриме"""
    stream, _, _ = permissions.check_stream_access(data_base, stream_id, user_id)
    return stream


def create_stream_service(data_base: Session, project_id: int, stream_data: stream_schemas.StreamCreate, user_id: int):
    """Создать новый стрим"""
    _, user_team = permissions.check_project_access(data_base, project_id, user_id)

    permissions.check_editor_permission(user_team)

    existing = stream_crud.get_stream_by_name_and_proj_id(data_base, stream_data.name, project_id)
    if existing:
        raise exception.ConflictError("В данном проекте уже есть стрим с таким названием")

    if stream_data.position is None:
        last_stream = data_base.query(stream_model.Stream).filter(
            stream_model.Stream.project_id == project_id
        ).order_by(stream_model.Stream.position.desc()).first()
        stream_data.position = (last_stream.position + 1) if last_stream else 1

    new_stream = stream_crud.create_new_stream(data_base, project_id, stream_data)
    return new_stream


def update_stream_service(data_base: Session, stream_id: int, update_data: stream_schemas.StreamUpdate, user_id: int):
    """Обновить стрим"""
    stream, _, user_team = permissions.check_stream_access(data_base, stream_id, user_id)

    permissions.check_editor_permission(user_team)

    updated_stream = stream_crud.update_stream(data_base, stream, update_data)
    return updated_stream


def delete_stream_service(data_base: Session, stream_id: int, user_id: int):
    """Удалить стрим"""
    _, _, user_team = permissions.check_stream_access(data_base, stream_id, user_id)

    permissions.check_editor_permission(user_team)

    stream_crud.delete_stream(data_base, stream_id)
