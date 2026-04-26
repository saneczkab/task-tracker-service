from sqlalchemy import orm

from app.models import task


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
    for field, value in task_update_data.model_dump(exclude_unset=True).items():
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
