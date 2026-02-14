from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from models import Project, UserTeam, User, Stream
from models.meta import UserTask
from models.task import Task
from schemas.task import TaskResponse, TaskCreate, TaskUpdate
from .auth import get_current_user

router = APIRouter()


@router.get("/api/project/{proj_id}/tasks", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_project_tasks(proj_id: int, current_user: User = Depends(get_current_user),
                      data_base: Session = Depends(get_db)):
    """Получить все задачи в проекте proj_id"""
    project = data_base.query(Project).filter(Project.id == proj_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()
    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к проекту")

    tasks = []

    for stream in project.streams:
        tasks.extend(stream.tasks)

    return tasks

@router.get("/api/stream/{stream_id}/tasks", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_stream_tasks(stream_id: int, current_user: User = Depends(get_current_user),
                     data_base: Session = Depends(get_db)):
    """Получить все задачи в стриме stream_id"""
    stream = data_base.query(Stream).filter(Stream.id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project = data_base.query(Project).filter(Project.id == stream.project_id).first()
    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к стриму")

    tasks = data_base.query(Task).filter(Task.stream_id == stream.id).all()

    for task in tasks:
        assignee = data_base.query(UserTask).filter(UserTask.task_id == task.id).first()
        if assignee:
            user = data_base.query(User).filter(User.id == assignee.user_id).first()
            task.assignee_email = user.email if user else None

    return tasks


@router.post("/api/stream/{stream_id}/task/new", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(stream_id: int, task_data: TaskCreate, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Создать задачу в стриме stream_id"""
    stream = data_base.query(Stream).filter(Stream.id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project = data_base.query(Project).filter(Project.id == stream.project_id).first()
    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к стриму")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на создание задачи")

    task = Task(
        name=task_data.name,
        description=task_data.description or "",
        stream_id=stream_id,
        status_id=task_data.status_id,
        priority_id=task_data.priority_id,
        start_date=task_data.start_date,
        deadline=task_data.deadline
    )

    data_base.add(task)
    data_base.flush()

    assignee_id = data_base.query(User.id).filter(User.email == task_data.assignee_email).first() if task_data.assignee_email else None
    if assignee_id:
        user_task = UserTask(
            user_id=assignee_id.id,
            task_id=task.id
        )
        data_base.add(user_task)

    data_base.commit()
    data_base.refresh(task)

    return task


@router.patch("/api/task/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_update_data: TaskUpdate, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Частично обновить данные о задаче task_id"""
    task = data_base.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    stream = data_base.query(Stream).filter(Stream.id == task.stream_id).first()
    project = data_base.query(Project).filter(Project.id == stream.project_id).first()
    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к задаче")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на редактирование задачи")

    if task_update_data.name is not None:
        task.name = task_update_data.name

    if task_update_data.description is not None:
        task.description = task_update_data.description

    if task_update_data.status_id is not None:
        task.status_id = task_update_data.status_id

    if task_update_data.priority_id is not None:
        task.priority_id = task_update_data.priority_id

    task.start_date = task_update_data.start_date
    task.deadline = task_update_data.deadline

    if task_update_data.assignee_email is not None:
        assigning_user = data_base.query(User).filter(User.email == task_update_data.assignee_email).first()
        if assigning_user:
            user_task = UserTask(
                user_id=data_base.query(User.id).filter(User.email == task_update_data.assignee_email).first().id,
                task_id=task_id
            )
            data_base.add(user_task)

        old_user_task = data_base.query(UserTask).filter(UserTask.task_id == task_id).first()
        if old_user_task:
            data_base.delete(old_user_task)

    data_base.commit()
    data_base.refresh(task)

    return task


@router.delete("/api/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    """Удалить задачу task_id"""
    task = data_base.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    stream = data_base.query(Stream).filter(Stream.id == task.stream_id).first()
    project = data_base.query(Project).filter(Project.id == stream.project_id).first()
    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к задаче")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на удаление задачи")

    user_task = data_base.query(UserTask).filter(UserTask.task_id == task_id).first()
    if user_task:
        data_base.delete(user_task)

    data_base.delete(task)
    data_base.commit()
