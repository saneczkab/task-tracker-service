from sqlalchemy import orm

from app.core import exception
from app.crud import task as task_crud, custom_field as custom_field_crud
from app.models import meta, project, task, team, user, tag, stream, custom_field
from app.services import permissions


def get_all_tasks_service(data_base: orm.Session, user_id: int):
    user_teams = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == user_id).all()

    if not user_teams:
        return []

    tasks = []

    for user_team in user_teams:
        team_projects = data_base.query(project.Project).filter(project.Project.team_id == user_team.team_id).all()

        for project_obj in team_projects:
            for stream_obj in project_obj.streams:
                stream_tasks = data_base.query(task.Task).filter(task.Task.stream_id == stream_obj.id).all()

                for task_obj in stream_tasks:
                    task_obj.team_id = project_obj.team_id
                    task_obj.team_name = project_obj.team.name if project_obj.team else None
                    task_obj.project_id = project_obj.id
                    task_obj.project_name = project_obj.name
                    task_obj.stream_name = stream_obj.name
                    tasks.append(task_obj)

                    if task_obj.assigned_users:
                        task_obj.assignee_email = task_obj.assigned_users[0].user.email

    return tasks


def get_project_tasks_service(data_base: orm.Session, project_id: int, user_id: int):
    project_obj = data_base.query(project.Project).filter(project.Project.id == project_id).first()
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == user_id).first()
    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к проекту")

    return task_crud.get_tasks_by_project(data_base, project_obj)


def get_stream_tasks_service(data_base: orm.Session, stream_id: int, user_id: int):
    permissions.check_stream_access(data_base, stream_id, user_id)
    return task_crud.get_tasks_by_stream(data_base, stream_id)


def create_task_service(data_base: orm.Session, stream_id: int, user_id: int, task_data):
    permissions.check_stream_access(data_base, stream_id, user_id, need_lead=True)

    if task_data.position is None:
        last_pos = data_base.query(task.Task).filter(task.Task.stream_id == stream_id).order_by(
            task.Task.position.desc()).first()
        task_data.position = (last_pos.position + 1) if last_pos else 1

    new_task = task_crud.create_task(data_base, stream_id, task_data)

    if task_data.assignee_email:
        assignee_user = data_base.query(user.User).filter(user.User.email == task_data.assignee_email).first()
        if not assignee_user:
            raise exception.NotFoundError("Пользователь не найден")

        data_base.add(meta.UserTask(user_id=assignee_user.id, task_id=new_task.id))

    if task_data.tag_ids:
        stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

        if not stream_obj:
            raise exception.NotFoundError("Стрим не найден")

        team_id = stream_obj.project.team_id

        for tag_id in task_data.tag_ids:

            tag_obj = data_base.query(tag.Tag).filter(tag.Tag.id == tag_id).first()

            if not tag_obj:
                raise exception.NotFoundError(f"Тег с id {tag_id} не найден")

            if tag_obj.team_id != team_id:
                raise exception.ForbiddenError("Тег принадлежит другой команде")

            data_base.add(tag.TaskTag(task_id=new_task.id, tag_id=tag_id))

    if task_data.custom_fields:
        for field_value in task_data.custom_fields:
            custom_field_crud.set_task_custom_field_value(data_base, new_task.id, field_value)

    data_base.commit()
    data_base.refresh(new_task)
    return new_task


def update_task_service(data_base: orm.Session, task_id: int, user_id: int, task_update_data):
    task_obj, stream_obj, project_obj, team_obj = permissions.check_task_access(data_base, task_id, user_id,
                                                                                need_lead=True)

    tracked_fields = ["name", "description", "status_id", "priority_id", "start_date", "deadline", "position"]
    changes = {}
    for field in tracked_fields:
        if field in task_update_data.model_fields_set:
            old_val = getattr(task_obj, field)
            new_val = getattr(task_update_data, field)
            if old_val != new_val:
                changes[field] = (old_val, new_val)

    if task_update_data.assignee_email is not None:
        old_assignee = task_obj.assigned_users[0].user.email if task_obj.assigned_users else None
        if old_assignee != task_update_data.assignee_email:
            changes["assignee_email"] = (old_assignee, task_update_data.assignee_email)

    if task_update_data.assignee_email:
        assignee_user = data_base.query(user.User).filter(user.User.email == task_update_data.assignee_email).first()
        if not assignee_user:
            raise exception.NotFoundError("Пользователь не найден")

        old_user_task = data_base.query(meta.UserTask).filter(meta.UserTask.task_id == task_id).first()
        if old_user_task:
            data_base.delete(old_user_task)

        data_base.add(meta.UserTask(user_id=assignee_user.id, task_id=task_id))

    if task_update_data.tag_ids is not None:
        old_tag_ids = [t.tag_id for t in task_obj.tags]
        new_tag_ids = task_update_data.tag_ids
        if old_tag_ids != new_tag_ids:
            changes["tag_ids"] = (old_tag_ids, new_tag_ids)

        data_base.query(tag.TaskTag).filter(tag.TaskTag.task_id == task_id).delete()

        for tag_id in task_update_data.tag_ids:

            tag_obj = data_base.query(tag.Tag).filter(tag.Tag.id == tag_id).first()

            if not tag_obj:
                raise exception.NotFoundError(f"Тег с id {tag_id} не найден")

            if tag_obj.team_id != team_obj.id:
                raise exception.ForbiddenError("Тег принадлежит другой команде")

            data_base.add(tag.TaskTag(task_id=task_id, tag_id=tag_id))

    if task_update_data.custom_fields is not None:
        old_custom_fields = {cf.custom_field_id: cf.value for cf in task_obj.custom_field_values}
        new_custom_fields = {cf.custom_field_id: cf.value for cf in task_update_data.custom_fields}
        if old_custom_fields != new_custom_fields:
            changes["custom_fields"] = (old_custom_fields, new_custom_fields)

        for field_value in task_update_data.custom_fields:
            custom_field_crud.set_task_custom_field_value(data_base, task_id, field_value)

    task_update_data_filtered = task_update_data.model_dump(exclude_unset=True, exclude={'custom_fields'})
    task_crud.update_task(data_base, task_obj, task_update_data_filtered)

    if changes:
        task_crud.create_task_history_entries(data_base, task_id, user_id, changes)
        data_base.commit()

    return task_obj


def delete_task_service(data_base: orm.Session, task_id: int, user_id: int):
    task_obj, _, _, _ = permissions.check_task_access(data_base, task_id, user_id, need_lead=True)
    old_user_task = data_base.query(meta.UserTask).filter(meta.UserTask.task_id == task_id).first()
    if old_user_task:
        data_base.delete(old_user_task)

    task_crud.delete_task(data_base, task_obj)


def delete_task_relation_service(db: orm.Session, relation_id: int, user_id: int):
    relation = db.query(task.TaskRelation).filter(task.TaskRelation.id == relation_id).first()

    if not relation:
        raise exception.NotFoundError("Связь не найдена")

    _, _, _, _ = permissions.check_task_access(db, relation.task_id_1, user_id, need_lead=True)

    db.delete(relation)
    db.commit()


def create_task_relation_service(data_base: orm.Session, task_id_1: int, task_id_2: int, connection_id: int):
    task_1 = task_crud.get_task_by_id(data_base, task_id_1)
    task_2 = task_crud.get_task_by_id(data_base, task_id_2)
    if not task_1 or not task_2:
        raise exception.NotFoundError("Одна из задач не найдена")
    if task_id_1 == task_id_2:
        raise exception.ConflictError("Нельзя создать связь задачи с самой собой")

    connection_type = data_base.query(meta.ConnectionType).filter(meta.ConnectionType.id == connection_id).first()
    if not connection_type:
        raise exception.NotFoundError("Тип связи не найден")

    return task_crud.create_task_relation(data_base, task_id_1, task_id_2, connection_id)


def get_task_history_service(data_base: orm.Session, task_id: int, user_id: int):
    """Получить историю изменений задачи."""
    task_obj, _, _, _ = permissions.check_task_access(data_base, task_id, user_id)
    history = task_crud.get_task_history(data_base, task_id)

    for entry in history:
        if entry.changed_by:
            entry.changed_by_email = entry.changed_by.email

    return history


def delete_task_custom_field_service(data_base: orm.Session, task_id: int, custom_field_id: int, user_id: int):
    """Удалить значение кастомного поля для задачи."""
    task_obj, _, _, team_obj = permissions.check_task_access(data_base, task_id, user_id, need_lead=True)

    custom_field_obj = data_base.query(custom_field.TaskCustomFieldValue).filter_by(
        task_id=task_id,
        custom_field_id=custom_field_id
    ).first()

    if not custom_field_obj:
        raise exception.NotFoundError()

    return custom_field_crud.delete_task_custom_field_value(data_base, task_id, custom_field_id)

