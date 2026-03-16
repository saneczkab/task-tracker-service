import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.core.scheduler import scheduler
from app.schemas import reminder as reminder_schemas
from app.services import reminder_service, push_service

router = fastapi.APIRouter(prefix="/api/tasks", tags=["Reminders"])


@router.get("/{task_id}/reminders", response_model=list[reminder_schemas.ReminderResponse])
def get_task_reminders(
    task_id: int,
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Получить напоминания для задачи"""
    try:
        return reminder_service.get_task_reminders_service(data_base, task_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.post("/{task_id}/reminders", response_model=reminder_schemas.ReminderResponse)
def create_reminder(
    task_id: int,
    reminder_data: reminder_schemas.ReminderCreate,
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Создать напоминание для задачи"""
    try:
        reminder = reminder_service.create_reminder_service(
            data_base, task_id, current_user.id, reminder_data
        )

        scheduler.add_job(
            push_service.send_push,
            "date",
            run_date=reminder.remind_at,
            args=[reminder.id],
            id=str(reminder.id)
        )

        return reminder
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(400, str(e))


@router.patch("/reminders/{reminder_id}", response_model=reminder_schemas.ReminderResponse)
def update_reminder(
    reminder_id: int,
    reminder_data: reminder_schemas.ReminderUpdate,
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Обновить напоминание"""
    try:
        reminder = reminder_service.update_reminder_service(
            data_base, reminder_id, current_user.id, reminder_data
        )

        if reminder_data.remind_at:
            if scheduler.get_job(str(reminder.id)):
                scheduler.remove_job(str(reminder.id))

            scheduler.add_job(
                push_service.send_push,
                "date",
                run_date=reminder.remind_at,
                args=[reminder.id],
                id=str(reminder.id)
            )

        return reminder
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(400, str(e))


@router.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: int,
    current_user=fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db),
):
    """Удалить напоминание"""
    try:
        reminder_service.delete_reminder_service(data_base, reminder_id, current_user.id)

        if scheduler.get_job(str(reminder_id)):
            scheduler.remove_job(str(reminder_id))

    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))
