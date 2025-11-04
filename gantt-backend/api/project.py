from typing import List

from sqlalchemy.orm import Session
from core.db import get_db
from models import Project, User, Team, UserTeam
from schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from .auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.get("/api/team/{team_id}/projects", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_team_projects(team_id: int, current_user: User = Depends(get_current_user),
                      data_base: Session = Depends(get_db)):
    """Получить все проекты в команде team_id"""
    team = data_base.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(UserTeam).filter(UserTeam.user_id == current_user.id,
                                                 UserTeam.team_id == team_id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой команде")

    projects = data_base.query(Project).filter(Project.team_id == team_id).all()

    return projects


@router.post("/api/team/{team_id}/project/new", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(team_id: int, project_data: ProjectCreate, current_user: User = Depends(get_current_user),
                   data_base: Session = Depends(get_db)):
    """Создать новый проект в команде team_id"""
    team = data_base.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(UserTeam).filter(UserTeam.user_id == current_user.id,
                                                 UserTeam.team_id == team_id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой команде")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на создание проектов в этой команде")

    project = data_base.query(Project).filter(Project.team_id == team_id, Project.name == project_data.name).first()

    if project:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="В данной команде уже есть проект с таким названием")

    new_project = Project(name=project_data.name, team_id=team_id)

    data_base.add(new_project)
    data_base.commit()
    data_base.refresh(new_project)

    return new_project


@router.patch("/api/project/{proj_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project(proj_id: int, project_update_data: ProjectUpdate, current_user: User = Depends(get_current_user),
                   data_base: Session = Depends(get_db)):
    """Частично обновить данные о проекте proj_id"""
    project = data_base.query(Project).filter(Project.id == proj_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(UserTeam).filter(UserTeam.user_id == current_user.id,
                                                 UserTeam.team_id == project.team.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Вы должны состоять в команде проекта")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на редактирование проекта")

    if project_update_data.name is not None:
        if project_update_data.name != project.name:
            existing_project = data_base.query(Project).filter(Project.team_id == project.team.id,
                                                               Project.name == project_update_data.name,
                                                               Project.id != proj_id).first()
            if existing_project:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Проект с таким названием уже существует в команде")

            project.name = project_update_data.name

    data_base.commit()
    data_base.refresh(project)

    return project


@router.delete("/api/project/{proj_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(proj_id: int, current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    """Удалить проект proj_id"""
    project = data_base.query(Project).filter(Project.id == proj_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(UserTeam).filter(UserTeam.user_id == current_user.id,
                                                 UserTeam.team_id == project.team.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Вы должны состоять в команде проекта")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на удаление проекта в этой команде")

    data_base.delete(project)
    data_base.commit()
