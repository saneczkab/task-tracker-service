from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from core.db import get_db
from models import User, Stream, Project, UserTeam, Goal
from .auth import get_current_user
from sqlalchemy.orm import Session
from schemas.goal import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter()


@router.get("/api/stream/{stream_id}/goals", response_model=List[GoalResponse], status_code=status.HTTP_200_OK)
def get_stream_goals(stream_id: int, current_user: User = Depends(get_current_user),
                     data_base: Session = Depends(get_db)):
    """Получить все цели у стрима stream_id"""
    stream = data_base.query(Stream).filter(Stream.id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project = data_base.query(Project).filter(Project.id == stream.project_id).first()

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этому стриму")

    goals = data_base.query(Goal).filter(Goal.stream_id == stream.id).all()

    return goals


@router.post("/api/stream/{stream_id}/goal/new", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(stream_id: int, goal_data: GoalCreate, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Создать цель в стриме stream_id"""
    stream = data_base.query(Stream).filter(Stream.id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project = data_base.query(Project).filter(Project.id == stream.project_id).first()

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этому стриму")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на создание целей в этом проекте")

    existing_goal = data_base.query(Goal).filter(Goal.stream_id == stream_id, Goal.name == goal_data.name).first()

    if existing_goal:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="В данном стриме уже есть цель с таким названием")

    new_goal = Goal(
        name=goal_data.name,
        stream_id=stream_id,
        description=goal_data.description,
        deadline=goal_data.deadline
    )

    data_base.add(new_goal)
    data_base.commit()
    data_base.refresh(new_goal)

    return new_goal


@router.patch("/api/goal/{goal_id}", response_model=GoalResponse, status_code=status.HTTP_200_OK)
def update_goal(goal_id: int, goal_update_data: GoalUpdate, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Частично обновить данные о цели goal_id"""
    goal = data_base.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Цель не найдена")

    stream = data_base.query(Stream).filter(Stream.id == goal.stream_id).first()
    project = data_base.query(Project).filter(Project.id == stream.project_id).first()

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой цели")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на редактирование целей в этом стриме")

    if goal_update_data.name is not None:
        if goal_update_data.name != goal.name:
            existing_goal = data_base.query(Goal).filter(Goal.name == goal_update_data.name,
                                                         Goal.stream_id == goal.stream.id,
                                                         Goal.id != goal_id).first()

            if existing_goal:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Цель с таким названием уже существует в стриме")

            goal.name = goal_update_data.name

    if goal_update_data.description is not None:
        goal.description = goal_update_data.description

    if goal_update_data.deadline is not None:
        goal.deadline = goal_update_data.deadline

    data_base.commit()
    data_base.refresh(goal)

    return goal


@router.delete("/api/goal/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Удалить цель goal_id"""
    goal = data_base.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Цель не найдена")

    stream = data_base.query(Stream).filter(Stream.id == goal.stream_id).first()
    project = data_base.query(Project).filter(Project.id == stream.project_id).first()

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой цели")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на удаление целей в этом стриме")

    data_base.delete(goal)
    data_base.commit()

