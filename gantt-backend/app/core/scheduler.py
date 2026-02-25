from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.db import SessionLocal
from app.crud import reminder as reminder_crud
from app.services import push_service

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.start()

    db = SessionLocal()
    reminders = reminder_crud.get_pending_reminders(db)

    for r in reminders:
        if r.remind_at > datetime.utcnow():
            scheduler.add_job(
                push_service.send_push,
                "date",
                run_date=r.remind_at,
                args=[r.id],
                id=str(r.id)
            )

    db.close()