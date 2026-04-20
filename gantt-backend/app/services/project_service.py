from sqlalchemy import orm

from app.core import exception
from app.crud import project as project_crud
from app.models import goal, stream, task
from app.services import permissions


def get_team_projects_service(data_base: orm.Session, team_id: int, user_id: int):
    permissions.check_team_access(data_base, team_id, user_id)
    return project_crud.get_projects_by_team(data_base, team_id)


def create_project_service(data_base: orm.Session, team_id: int, user_id: int, project_data):
    permissions.check_team_access(data_base, team_id, user_id, need_lead=True)
    return project_crud.create_project(data_base, team_id, project_data)


def update_project_service(data_base: orm.Session, proj_id: int, user_id: int, update_data):
    project_obj, _ = permissions.check_project_access(data_base, proj_id, user_id, need_lead=True)
    return project_crud.update_project(data_base, project_obj, update_data)


def delete_project_service(data_base: orm.Session, proj_id: int, user_id: int):
    project_obj, _ = permissions.check_project_access(data_base, proj_id, user_id, need_lead=True)
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    streams = data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).all()
    stream_ids = [s.id for s in streams]

    if stream_ids:
        data_base.query(task.Task).filter(task.Task.stream_id.in_(stream_ids)).delete(synchronize_session=False)
        data_base.query(goal.Goal).filter(goal.Goal.stream_id.in_(stream_ids)).delete(synchronize_session=False)
        data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).delete(synchronize_session=False)

    project_crud.delete_project(data_base, project_obj)
