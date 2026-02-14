from sqlalchemy import orm

from app.core import exception
from app.crud import goal as goal_crud
from app.models import goal, project, role, stream, team


def check_stream_permissions(data_base: orm.Session, stream_id: int, user_id: int, need_lead: bool = False):
    """Общий метод проверки прав на стрим/проект."""
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()
    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == user_id).first()

    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к этому стриму")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение этого действия")

    return stream_obj


def get_stream_goals_service(data_base: orm.Session, stream_id: int, user_id: int):
    check_stream_permissions(data_base, stream_id, user_id)
    return goal_crud.get_goals_by_stream(data_base, stream_id)


def create_goal_service(data_base: orm.Session, stream_id: int, user_id: int, goal_data):
    check_stream_permissions(data_base, stream_id, user_id, need_lead=True)

    if goal_crud.get_goal_by_name_in_stream(data_base, stream_id, goal_data.name):
        raise exception.ConflictError("В данном стриме уже есть цель с таким названием")

    if goal_data.position is None:
        last = data_base.query(goal.Goal).filter_by(stream_id=stream_id).order_by(
            goal.Goal.position.desc()).first()
        goal_data.position = (last.position + 1) if last else 1

    return goal_crud.create_goal(data_base, stream_id, goal_data)


def update_goal_service(data_base: orm.Session, goal_id: int, user_id: int, goal_update_data):
    goal_obj = goal_crud.get_goal_by_id(data_base, goal_id)
    if not goal_obj:
        raise exception.NotFoundError("Цель не найдена")

    check_stream_permissions(data_base, goal_obj.stream_id, user_id, need_lead=True)

    if goal_update_data.name:
        if goal_update_data.name != goal_obj.name:
            existing = goal_crud.get_goal_by_name_in_stream(
                data_base,
                goal_obj.stream_id,
                goal_update_data.name,
                exclude_id=goal_id
            )
            if existing:
                raise exception.ConflictError("Цель с таким названием уже существует в стриме")

    return goal_crud.update_goal(data_base, goal_obj, goal_update_data)


def delete_goal_service(data_base: orm.Session, goal_id: int, user_id: int):
    goal_obj = goal_crud.get_goal_by_id(data_base, goal_id)
    if not goal_obj:
        raise exception.NotFoundError("Цель не найдена")

    check_stream_permissions(data_base, goal_obj.stream_id, user_id, need_lead=True)

    goal_crud.delete_goal(data_base, goal_obj)
