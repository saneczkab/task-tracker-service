import typing
import fastapi
from sqlalchemy import orm
from app.core import db
from app.models import project, team, user, stream, meta, task
from app.schemas import task as task_schemas
from app.api import auth

router = fastapi.APIRouter()


@router.get("/api/project/{proj_id}/tasks", response_model=typing.List[task_schemas.TaskResponse],
            status_code=fastapi.status.HTTP_200_OK)
def get_project_tasks(proj_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                      data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все задачи в проекте proj_id"""
    project_obj = data_base.query(project.Project).filter(project.Project.id == proj_id).first()

    if not project_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == current_user.id).first()
    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к проекту")

    tasks = []

    for stream_obj in project_obj.streams:
        tasks.extend(stream_obj.tasks)

    return tasks


@router.get("/api/stream/{stream_id}/tasks", response_model=typing.List[task_schemas.TaskResponse],
            status_code=fastapi.status.HTTP_200_OK)
def get_stream_tasks(stream_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                     data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все задачи в стриме stream_id"""
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

    if not stream_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к стриму")

    tasks = data_base.query(task.Task).filter(task.Task.stream_id == stream_obj.id).all()

    return tasks


@router.post("/api/stream/{stream_id}/task/new", response_model=task_schemas.TaskResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
def create_task(stream_id: int, task_data: task_schemas.TaskCreate,
                current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Создать задачу в стриме stream_id"""
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

    if not stream_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к стриму")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на создание задачи")

    task_obj = task.Task(
        name=task_data.name,
        description=task_data.description or "",
        stream_id=stream_id,
        status_id=task_data.status_id or 1,
        priority_id=task_data.priority_id or 1,
        start_date=task_data.start_date,
        deadline=task_data.deadline
    )

    data_base.add(task_obj)
    data_base.commit()
    data_base.refresh(task_obj)

    return task_obj


@router.patch("/api/task/{task_id}", response_model=task_schemas.TaskResponse, status_code=fastapi.status.HTTP_200_OK)
def update_task(task_id: int, task_update_data: task_schemas.TaskUpdate,
                current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о задаче task_id"""
    task_obj = data_base.query(task.Task).filter(task.Task.id == task_id).first()

    if not task_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == task_obj.stream_id).first()
    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к задаче")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на редактирование задачи")

    if task_update_data.name is not None:
        task_obj.name = task_update_data.name

    if task_update_data.description is not None:
        task_obj.description = task_update_data.description

    if task_update_data.status_id is not None:
        task_obj.status_id = task_update_data.status_id

    if task_update_data.priority_id is not None:
        task_obj.priority_id = task_update_data.priority_id

    task_obj.start_date = task_update_data.start_date
    task_obj.deadline = task_update_data.deadline

    if task_update_data.assignee_email is not None:
        assigning_user = data_base.query(user.User).filter(user.User.email == task_update_data.assignee_email).first()
        if assigning_user:
            user_task = meta.UserTask(
                user_id=assigning_user.id,
                task_id=task_id
            )
            data_base.add(user_task)

        old_user_task = data_base.query(meta.UserTask).filter(meta.UserTask.task_id == task_id).first()
        if old_user_task:
            data_base.delete(old_user_task)

    data_base.commit()
    data_base.refresh(task_obj)

    return task_obj


@router.delete("/api/task/{task_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить задачу task_id"""
    task_obj = data_base.query(task.Task).filter(task.Task.id == task_id).first()

    if not task_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == task_obj.stream_id).first()
    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team.id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к задаче")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на удаление задачи")

    user_task = data_base.query(meta.UserTask).filter(meta.UserTask.task_id == task_id).first()
    if user_task:
        data_base.delete(user_task)

    data_base.delete(task_obj)
    data_base.commit()
