from sqlalchemy import orm

from app.models import task


def get_reminder_by_id(db: orm.Session, reminder_id: int):
    """Получить напоминание по id"""
    return db.query(task.TaskReminder).filter(task.TaskReminder.id == reminder_id).first()


def get_reminders_by_task_and_user(db: orm.Session, task_id: int, user_id: int):
    """Получить напоминания по задаче и пользователю"""
    return db.query(task.TaskReminder).filter(
        task.TaskReminder.task_id == task_id,
        task.TaskReminder.user_id == user_id
    ).all()


def get_reminders_by_user(db: orm.Session, user_id: int):
    """Получить все напоминания пользователя"""
    return db.query(task.TaskReminder).filter(
        task.TaskReminder.user_id == user_id
    ).all()


def get_pending_reminders(db: orm.Session):
    """Получить все напоминания, которые нужно отправить"""
    return db.query(task.TaskReminder).filter(
        task.TaskReminder.sent == False
    ).all()


def create_reminder(db: orm.Session, task_id: int, user_id: int, remind_at):
    """Создать напоминание"""
    reminder = task.TaskReminder(
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at
    )
    db.add(reminder)
    db.flush()
    return reminder


def update_reminder(db: orm.Session, reminder_obj, reminder_update_data):
    """Обновить напоминание"""
    for field, value in reminder_update_data.model_dump(exclude_unset=True).items():
        setattr(reminder_obj, field, value)
    db.commit()
    db.refresh(reminder_obj)
    return reminder_obj


def mark_as_sent(db: orm.Session, reminder_obj):
    """Отметить напоминание как отправленное"""
    reminder_obj.sent = True
    db.commit()
    db.refresh(reminder_obj)
    return reminder_obj


def delete_reminder(db: orm.Session, reminder_obj):
    """Удалить напоминание"""
    db.delete(reminder_obj)
    db.commit()

