from sqlalchemy import orm

from app.core import exception
from app.crud import task as task_crud
from app.models import meta, project, role, stream, task, team, user


def check_stream_permissions(data_base: orm.Session, stream_id: int, user_id: int, need_lead=False):
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()
    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == user_id).first()
    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к стриму")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение действия")

    return stream_obj


def check_task_permissions(data_base: orm.Session, task_id: int, user_id: int, need_lead=False):
    task_obj = task_crud.get_task_by_id(data_base, task_id)
    if not task_obj:
        raise exception.NotFoundError("Задача не найдена")

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == task_obj.stream_id).first()
    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    if not project_obj:
        raise exception.NotFoundError("Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == user_id).first()
    if not user_team:
        raise exception.ForbiddenError("У вас нет доступа к задаче")

    if need_lead and user_team.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("У вас нет прав на выполнение действия")

    return task_obj


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
    check_stream_permissions(data_base, stream_id, user_id)
    return task_crud.get_tasks_by_stream(data_base, stream_id)


def create_task_service(data_base: orm.Session, stream_id: int, user_id: int, task_data):
    check_stream_permissions(data_base, stream_id, user_id, need_lead=True)

    if task_data.position is None:
        last_pos = data_base.query(task.Task).filter(task.Task.stream_id == stream_id).order_by(task.Task.position.desc()).first()
        task_data.position = (last_pos.position + 1) if last_pos else 1

    new_task = task_crud.create_task(data_base, stream_id, task_data)

    if task_data.assignee_email:
        assignee_user = data_base.query(user.User).filter(user.User.email == task_data.assignee_email).first()
        if not assignee_user:
            raise exception.NotFoundError("Пользователь не найден")

        data_base.add(meta.UserTask(user_id=assignee_user.id, task_id=new_task.id))

    data_base.commit()
    data_base.refresh(new_task)
    return new_task


def update_task_service(data_base: orm.Session, task_id: int, user_id: int, task_update_data):
    task_obj = check_task_permissions(data_base, task_id, user_id, need_lead=True)

    if task_update_data.assignee_email:
        assignee_user = data_base.query(user.User).filter(user.User.email == task_update_data.assignee_email).first()
        if not assignee_user:
            raise exception.NotFoundError("Пользователь не найден")

        old_user_task = data_base.query(meta.UserTask).filter(meta.UserTask.task_id == task_id).first()
        if old_user_task:
            data_base.delete(old_user_task)

        data_base.add(meta.UserTask(user_id=assignee_user.id, task_id=task_id))

    task_crud.update_task(data_base, task_obj, task_update_data)
    return task_obj


def delete_task_service(data_base: orm.Session, task_id: int, user_id: int):
    task_obj = check_task_permissions(data_base, task_id, user_id, need_lead=True)
    old_user_task = data_base.query(meta.UserTask).filter(meta.UserTask.task_id == task_id).first()
    if old_user_task:
        data_base.delete(old_user_task)

    task_crud.delete_task(data_base, task_obj)


def delete_task_relation_service(db: orm.Session, relation_id: int, user_id: int):
    relation = db.query(task.TaskRelation).filter(task.TaskRelation.id == relation_id).first()

    if not relation:
        raise exception.NotFoundError("Связь не найдена")

    check_task_permissions(db, relation.task_id_1, user_id, need_lead=True)

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
