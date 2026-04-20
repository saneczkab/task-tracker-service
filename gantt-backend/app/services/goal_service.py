from sqlalchemy import orm

from app.core import exception
from app.crud import goal as goal_crud
from app.models import goal
from app.services import permissions


def get_stream_goals_service(data_base: orm.Session, stream_id: int, user_id: int):
    permissions.check_stream_access(data_base, stream_id, user_id)
    return goal_crud.get_goals_by_stream(data_base, stream_id)


def create_goal_service(data_base: orm.Session, stream_id: int, user_id: int, goal_data):
    permissions.check_stream_access(data_base, stream_id, user_id, need_lead=True)

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

    permissions.check_stream_access(data_base, goal_obj.stream_id, user_id, need_lead=True)

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

    permissions.check_stream_access(data_base, goal_obj.stream_id, user_id, need_lead=True)

    goal_crud.delete_goal(data_base, goal_obj)
