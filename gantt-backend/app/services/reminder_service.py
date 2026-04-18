from datetime import datetime

from sqlalchemy import orm

from app.core import exception
from app.crud import reminder as reminder_crud
from app.services import permissions


def get_user_reminders_service(data_base: orm.Session, user_id: int):
    """Получить все напоминания пользователя"""
    return reminder_crud.get_reminders_by_user(data_base, user_id)


def get_task_reminders_service(data_base: orm.Session, task_id: int, user_id: int):
    """Получить напоминания по задаче"""
    _, _, _, _ = permissions.check_task_access(data_base, task_id, user_id)
    return reminder_crud.get_reminders_by_task_and_user(data_base, task_id, user_id)


def create_reminder_service(
    data_base: orm.Session,
    task_id: int,
    user_id: int,
    reminder_data
):
    """Создать напоминание"""
    _, _, _, _ = permissions.check_task_access(data_base, task_id, user_id)

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

