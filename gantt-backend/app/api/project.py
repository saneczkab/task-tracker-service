import typing
import fastapi
from sqlalchemy import orm
from app.core import db
from app.models import project, user, team, stream
from app.schemas import project as project_schemas
from app.api import auth

router = fastapi.APIRouter()


@router.get("/api/team/{team_id}/projects", response_model=typing.List[project_schemas.ProjectResponse],
            status_code=fastapi.status.HTTP_200_OK)
def get_team_projects(team_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                      data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все проекты в команде team_id"""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()

    if not team_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == current_user.id,
                                                      team.UserTeam.team_id == team_id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этой команде")

    projects = data_base.query(project.Project).filter(project.Project.team_id == team_id).all()

    return projects


@router.post("/api/team/{team_id}/project/new", response_model=project_schemas.ProjectResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
def create_project(team_id: int, project_data: project_schemas.ProjectCreate,
                   current_user: user.User = fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Создать новый проект в команде team_id"""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()

    if not team_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == current_user.id,
                                                      team.UserTeam.team_id == team_id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этой команде")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на создание проектов в этой команде")

    new_project = project.Project(name=project_data.name, team_id=team_id)

    data_base.add(new_project)
    data_base.commit()
    data_base.refresh(new_project)

    return new_project


@router.patch("/api/project/{proj_id}", response_model=project_schemas.ProjectResponse,
              status_code=fastapi.status.HTTP_200_OK)
def update_project(proj_id: int, project_update_data: project_schemas.ProjectUpdate,
                   current_user: user.User = fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о проекте proj_id"""
    project_obj = data_base.query(project.Project).filter(project.Project.id == proj_id).first()

    if not project_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == current_user.id,
                                                      team.UserTeam.team_id == project_obj.team_id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="Вы должны состоять в команде проекта")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на редактирование проекта")

    if project_update_data.name is not None:
        if project_update_data.name != project_obj.name:
            project_obj.name = project_update_data.name

    data_base.commit()
    data_base.refresh(project_obj)

    return project_obj


@router.delete("/api/project/{proj_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_project(proj_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить проект proj_id"""
    project_obj = data_base.query(project.Project).filter(project.Project.id == proj_id).first()

    if not project_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == current_user.id,
                                                      team.UserTeam.team_id == project_obj.team_id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="Вы должны состоять в команде проекта")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на удаление проекта в этой команде")

    data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).delete(synchronize_session=False)
    data_base.delete(project_obj)
    data_base.commit()
