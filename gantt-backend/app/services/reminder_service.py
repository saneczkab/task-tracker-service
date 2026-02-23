from datetime import datetime

from sqlalchemy import orm

from app.core import exception
from app.crud import reminder as reminder_crud
from app.crud import task as task_crud
from app.models import project, stream, team


def check_task_permissions(data_base: orm.Session, task_id: int, user_id: int):
    """Проверить доступ пользователя к задаче"""
    task_obj = task_crud.get_task_by_id(data_base, task_id)
    if not task_obj:
        raise exception.NotFoundError("Задача не найдена")

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == task_obj.stream_id).first()
    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(
        team.UserTeam.team_id == project_obj.team.id,
        team.UserTeam.user_id == user_id
    ).first()
    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к задаче")

    return task_obj


def get_user_reminders_service(data_base: orm.Session, user_id: int):
    """Получить все напоминания пользователя"""
    return reminder_crud.get_reminders_by_user(data_base, user_id)


def get_task_reminders_service(data_base: orm.Session, task_id: int, user_id: int):
    """Получить напоминания по задаче"""
    check_task_permissions(data_base, task_id, user_id)
    return reminder_crud.get_reminders_by_task_and_user(data_base, task_id, user_id)


def create_reminder_service(
    data_base: orm.Session,
    task_id: int,
    user_id: int,
    reminder_data
):
    """Создать напоминание"""
    check_task_permissions(data_base, task_id, user_id)

    if reminder_data.remind_at < datetime.utcnow():
        raise exception.ConflictError("Время напоминания не может быть в прошлом")

    reminder = reminder_crud.create_reminder(
        data_base,
        task_id=task_id,
        user_id=user_id,
        remind_at=reminder_data.remind_at
    )
    data_base.commit()
    data_base.refresh(reminder)
    return reminder


def update_reminder_service(
    data_base: orm.Session,
    reminder_id: int,
    user_id: int,
    reminder_data
):
    """Обновить напоминание"""
    reminder = reminder_crud.get_reminder_by_id(data_base, reminder_id)
    if not reminder:
        raise exception.NotFoundError("Напоминание не найдено")

    if reminder.user_id != user_id:
        raise exception.ForbiddenError("Вы не можете изменить это напоминание")

    if reminder_data.remind_at and reminder_data.remind_at < datetime.utcnow():
        raise exception.ConflictError("Время напоминания не может быть в прошлом")

    return reminder_crud.update_reminder(data_base, reminder, reminder_data)


def delete_reminder_service(data_base: orm.Session, reminder_id: int, user_id: int):
    """Удалить напоминание"""
    reminder = reminder_crud.get_reminder_by_id(data_base, reminder_id)
    if not reminder:
        raise exception.NotFoundError("Напоминание не найдено")

    if reminder.user_id != user_id:
        raise exception.ForbiddenError("Вы не можете удалить это напоминание")

    reminder_crud.delete_reminder(data_base, reminder)

