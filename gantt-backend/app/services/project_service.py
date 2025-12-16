from sqlalchemy import orm

from app.core import exception
from app.crud import project as project_crud
from app.models import goal, role, stream, task, team


def check_team_permissions(data_base: orm.Session, team_id: int, user_id: int, need_lead: bool = False):
    """Общая проверка прав на команду."""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()
    if not team_obj:
        raise exception.NotFoundError("Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                      team.UserTeam.user_id == user_id).first()
    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к этой команде")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение этого действия")

    return user_team


def check_project_permissions(data_base: orm.Session, proj_id: int, user_id: int, need_lead: bool = False):
    """Проверка доступа к проекту."""
    project_obj = project_crud.get_project_by_id(data_base, proj_id)
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == user_id).first()
    if not user_team:
        raise exception.ForbiddenError("Вы должны состоять в команде проекта")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение этого действия")

    return project_obj


def get_team_projects_service(data_base: orm.Session, team_id: int, user_id: int):
    check_team_permissions(data_base, team_id, user_id)
    return project_crud.get_projects_by_team(data_base, team_id)


def create_project_service(data_base: orm.Session, team_id: int, user_id: int, project_data):
    check_team_permissions(data_base, team_id, user_id, need_lead=True)
    return project_crud.create_project(data_base, team_id, project_data)


def update_project_service(data_base: orm.Session, proj_id: int, user_id: int, update_data):
    project_obj = check_project_permissions(data_base, proj_id, user_id, need_lead=True)
    return project_crud.update_project(data_base, project_obj, update_data)


def delete_project_service(data_base: orm.Session, proj_id: int, user_id: int):
    project_obj = check_project_permissions(data_base, proj_id, user_id, need_lead=True)
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    streams = data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).all()
    stream_ids = [s.id for s in streams]

    if stream_ids:
        data_base.query(task.Task).filter(task.Task.stream_id.in_(stream_ids)).delete(synchronize_session=False)
        data_base.query(goal.Goal).filter(goal.Goal.stream_id.in_(stream_ids)).delete(synchronize_session=False)
        data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).delete(synchronize_session=False)

    project_crud.delete_project(data_base, project_obj)
