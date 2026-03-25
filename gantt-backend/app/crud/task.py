from datetime import datetime

from sqlalchemy import orm

from app.models import task, team, project as project_model, stream as stream_model, user as user_model


def get_task_by_id(db: orm.Session, task_id: int):
    return db.query(task.Task).filter(task.Task.id == task_id).first()


def get_tasks_by_stream(db: orm.Session, stream_id: int):
    tasks = db.query(task.Task).filter(task.Task.stream_id == stream_id).all()
    for task_obj in tasks:
        if task_obj.assigned_users:
            task_obj.assignee_email = task_obj.assigned_users[0].user.email

    return tasks


def get_tasks_by_project(db: orm.Session, project_obj):
    tasks = []
    for stream_obj in project_obj.streams:
        stream_tasks = db.query(task.Task).filter(task.Task.stream_id == stream_obj.id).all()
        tasks.extend(stream_tasks)

    for task_obj in tasks:
        if task_obj.assigned_users:
            task_obj.assignee_email = task_obj.assigned_users[0].user.email

    return tasks


def create_task(db: orm.Session, stream_id: int, task_data):
    new_task = task.Task(
        name=task_data.name,
        description=task_data.description or "",
        stream_id=stream_id,
        status_id=task_data.status_id or 1,
        priority_id=task_data.priority_id or 1,
        start_date=task_data.start_date,
        deadline=task_data.deadline,
        position=task_data.position
    )
    db.add(new_task)
    db.flush()
    return new_task


def update_task(db: orm.Session, task_obj, task_update_data):
    for field, value in task_update_data.items():
        setattr(task_obj, field, value)
    db.commit()
    db.refresh(task_obj)
    return task_obj


def delete_task(db: orm.Session, task_obj):
    db.delete(task_obj)
    db.commit()


def create_task_relation(db: orm.Session, task_id_1: int, task_id_2: int, connection_id: int):
    relation = task.TaskRelation(
        task_id_1=task_id_1,
        task_id_2=task_id_2,
        connection_id=connection_id
    )
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation


def create_task_history_entries(db: orm.Session, task_id: int, changed_by_id: int, changes: dict):
    """Записать изменения в историю задачи."""
    entries = []
    now = datetime.utcnow()
    for field_name, (old_value, new_value) in changes.items():
        entry = task.TaskHistory(
            task_id=task_id,
            changed_by_id=changed_by_id,
            changed_at=now,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
        )
        db.add(entry)
        entries.append(entry)
    return entries


def get_task_history(db: orm.Session, task_id: int):
    """Получить историю изменений задачи."""
    return (
        db.query(task.TaskHistory)
        .filter(task.TaskHistory.task_id == task_id)
        .order_by(task.TaskHistory.changed_at.desc())
        .all()
    )


def get_tasks_by_user_id(db: orm.Session, user_id: int, only_assigned_to_user: bool = False):
    user_teams = db.query(team.UserTeam).filter(team.UserTeam.user_id == user_id).all()
    team_ids = [ut.team_id for ut in user_teams]
    projects = db.query(project_model.Project).filter(project_model.Project.team_id.in_(team_ids)).all()
    project_ids = [p.id for p in projects]
    streams = db.query(stream_model.Stream).filter(stream_model.Stream.project_id.in_(project_ids)).all()
    stream_ids = [s.id for s in streams]
    query = db.query(task.Task).filter(task.Task.stream_id.in_(stream_ids))
    if only_assigned_to_user:
        query = query.filter(task.Task.assigned_users.any(user_model.User.id == user_id))
    return query.all()


def get_tasks_by_team_id(db: orm.Session, team_id: int, user_id: int | None = None):
    projects = db.query(project_model.Project).filter(project_model.Project.team_id == team_id).all()
    project_ids = [p.id for p in projects]
    streams = db.query(stream_model.Stream).filter(stream_model.Stream.project_id.in_(project_ids)).all()
    stream_ids = [s.id for s in streams]
    query = db.query(task.Task).filter(task.Task.stream_id.in_(stream_ids))
    if user_id:
        query = query.filter(task.Task.assigned_users.any(user_model.User.id == user_id))
    return query.all()


def get_tasks_by_stream_id(db: orm.Session, stream_id: int, user_id: int | None = None):
    query = db.query(task.Task).filter(task.Task.stream_id == stream_id)
    if user_id:
        query = query.filter(task.Task.assigned_users.any(user_model.User.id == user_id))
    return query.all()

