import datetime
import ics

from sqlalchemy import orm
from app.crud.task import get_tasks_by_user_id, get_tasks_by_team_id, get_tasks_by_stream_id, \
    get_tasks_by_team_ids, get_tasks_by_project_ids, get_tasks_by_stream_ids
from app.schemas import calendar


def export_calendar_service(data_base: orm.Session, user_id: int, export_options: calendar.CalendarExport) -> str:
    tasks = []
    if export_options.target == "all":
        tasks = get_tasks_by_user_id(data_base, user_id, export_options.scope == "my")
    elif export_options.target == "team":
        tasks = get_tasks_by_team_id(data_base, export_options.target_id,
                                     user_id if export_options.scope == "my" else None)
    elif export_options.target == "stream":
        tasks = get_tasks_by_stream_id(data_base, export_options.target_id,
                                       user_id if export_options.scope == "my" else None)
    elif export_options.target == "teams":
        tasks = get_tasks_by_team_ids(data_base, export_options.target_ids,
                                      user_id if export_options.scope == "my" else None)
    elif export_options.target == "projects":
        tasks = get_tasks_by_project_ids(data_base, export_options.target_ids,
                                         user_id if export_options.scope == "my" else None)
    elif export_options.target == "streams":
        tasks = get_tasks_by_stream_ids(data_base, export_options.target_ids,
                                        user_id if export_options.scope == "my" else None)

    clndr = ics.Calendar()
    for task in tasks:
        event = ics.Event()
        event.name = task.name
        event.description = task.description

        if task.start_date and task.deadline:
            event.begin = task.start_date
            event.end = task.deadline
        elif task.start_date:
            event.begin = task.start_date
            event.end = task.start_date + datetime.timedelta(hours=1)
        elif task.deadline:
            event.begin = task.deadline - datetime.timedelta(hours=1)
            event.end = task.deadline
        else:
            event.begin = datetime.date.today()
            event.make_all_day()

        clndr.events.add(event)

    return str(clndr)
