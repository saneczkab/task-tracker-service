from sqlalchemy import orm

from app.core import exception
from app.crud import project as project_crud
from app.crud import stream as stream_crud
from app.crud import task as task_crud
from app.models import role, team


def check_team_access(data_base: orm.Session, team_id: int, user_id: int, need_lead: bool = False):
    """Проверить, что пользователь имеет доступ к команде."""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()
    if not team_obj:
        raise exception.NotFoundError("Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(
        team.UserTeam.team_id == team_id,
        team.UserTeam.user_id == user_id
    ).first()

    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к этой команде")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение этого действия")

    return team_obj, user_team


def check_project_access(data_base: orm.Session, project_id: int, user_id: int, need_lead: bool = False):
    """Проверить, что пользователь имеет доступ к проекту."""
    project_obj = project_crud.get_project_by_id(data_base, project_id)
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(
        team.UserTeam.team_id == project_obj.team_id,
        team.UserTeam.user_id == user_id
    ).first()

    if not user_team:
        raise exception.ForbiddenError("Вы должны состоять в команде проекта")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение этого действия")

    return project_obj, user_team


def check_stream_access(data_base: orm.Session, stream_id: int, user_id: int, need_lead: bool = False):
    """Проверить, что пользователь имеет доступ к стриму."""
    stream_obj = stream_crud.get_stream_by_id(data_base, stream_id)
    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")

    project_obj, user_team = check_project_access(data_base, stream_obj.project_id, user_id, need_lead=need_lead)

    return stream_obj, project_obj, user_team


def check_task_access(data_base: orm.Session, task_id: int, user_id: int, need_lead: bool = False):
    """Проверить, что пользователь имеет доступ к задаче."""
    task_obj = task_crud.get_task_by_id(data_base, task_id)
    if not task_obj:
        raise exception.NotFoundError("Задача не найдена")

    stream_obj, project_obj, user_team = check_stream_access(data_base, task_obj.stream_id, user_id, need_lead=need_lead)

    return task_obj, stream_obj, project_obj, user_team


def check_editor_permission(user_team):
    """Проверить, что у пользователя права редактора."""
    if user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав редактора для этого действия")

