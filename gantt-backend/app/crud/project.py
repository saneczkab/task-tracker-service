from sqlalchemy import orm

from app.models import custom_field as cf_model
from app.models import goal, project
from app.models import meta as meta_model
from app.models import stream as stream_model
from app.models import tag as tag_model
from app.models import task as task_model
from app.models.task import TaskRelation, TaskReminder


def get_project_by_id(data_base: orm.Session, project_id: int):
    """Получить проект по project_id"""
    return (
        data_base.query(project.Project)
        .filter(project.Project.id == project_id)
        .first()
    )


def get_projects_by_team(data_base: orm.Session, team_id: int):
    return (
        data_base.query(project.Project)
        .filter(project.Project.team_id == team_id)
        .order_by(project.Project.position)
        .all()
    )


def create_project(data_base: orm.Session, team_id: int, project_data):
    max_position = (
        data_base.query(project.Project)
        .filter(project.Project.team_id == team_id)
        .count()
    )

    new_project = project.Project(
        name=project_data.name, team_id=team_id, position=max_position
    )
    data_base.add(new_project)
    data_base.commit()
    data_base.refresh(new_project)
    return new_project


def update_project(data_base: orm.Session, project_obj, update_data):
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(project_obj, field, value)
    data_base.commit()
    data_base.refresh(project_obj)
    return project_obj


def delete_project(data_base: orm.Session, project_obj):
    data_base.delete(project_obj)
    data_base.commit()


def delete_project_with_dependencies(data_base: orm.Session, project_id: int):
    """Удалить проект со всеми стримами, задачами и их зависимостями"""
    streams = (
        data_base.query(stream_model.Stream)
        .filter(stream_model.Stream.project_id == project_id)
        .all()
    )
    stream_ids = [s.id for s in streams]

    if stream_ids:
        all_tasks = (
            data_base.query(task_model.Task)
            .filter(task_model.Task.stream_id.in_(stream_ids))
            .all()
        )
        task_ids = [t.id for t in all_tasks]

        if task_ids:
            data_base.query(task_model.TaskHistory).filter(
                task_model.TaskHistory.task_id.in_(task_ids)
            ).delete(synchronize_session=False)

            data_base.query(TaskReminder).filter(
                TaskReminder.task_id.in_(task_ids)
            ).delete(synchronize_session=False)

            data_base.query(TaskRelation).filter(
                (TaskRelation.task_id_1.in_(task_ids))
                | (TaskRelation.task_id_2.in_(task_ids))
            ).delete(synchronize_session=False)

            data_base.query(cf_model.TaskCustomFieldValue).filter(
                cf_model.TaskCustomFieldValue.task_id.in_(task_ids)
            ).delete(synchronize_session=False)

            data_base.query(tag_model.TaskTag).filter(
                tag_model.TaskTag.task_id.in_(task_ids)
            ).delete(synchronize_session=False)

            data_base.query(meta_model.UserTask).filter(
                meta_model.UserTask.task_id.in_(task_ids)
            ).delete(synchronize_session=False)

        data_base.query(task_model.Task).filter(
            task_model.Task.stream_id.in_(stream_ids)
        ).delete(synchronize_session=False)

        data_base.query(goal.Goal).filter(goal.Goal.stream_id.in_(stream_ids)).delete(
            synchronize_session=False
        )

        data_base.query(stream_model.Stream).filter(
            stream_model.Stream.project_id == project_id
        ).delete(synchronize_session=False)

    project_obj = (
        data_base.query(project.Project)
        .filter(project.Project.id == project_id)
        .first()
    )

    if project_obj:
        data_base.delete(project_obj)
        data_base.commit()


def reorder_projects(data_base: orm.Session, project_ids: list[int]):
    """Обновить позиции проектов согласно порядку в списке"""
    for idx, project_id in enumerate(project_ids):
        data_base.query(project.Project).filter(
            project.Project.id == project_id
        ).update({"position": idx})
    data_base.commit()
