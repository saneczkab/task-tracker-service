import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.schemas import project as project_schemas
from app.schemas import team as team_schemas
from app.services import project_service, team_service, task_service

router = fastapi.APIRouter()


@router.post("/api/team/new", response_model=team_schemas.TeamResponse, status_code=201)
def create_team(team_data: team_schemas.TeamCreate, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return team_service.create_team_service(data_base, current_user.id, team_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))


@router.patch("/api/team/{team_id}", response_model=team_schemas.TeamResponse)
def update_team(team_id: int, team_data: team_schemas.TeamUpdate,
                current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return team_service.update_team_service(data_base, team_id, current_user.id, team_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.delete("/api/team/{team_id}", status_code=204)
def delete_team(team_id: int, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        team_service.delete_team_service(data_base, team_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.get("/api/team/{team_id}/users", response_model=list[team_schemas.UserWithRoleResponse])
def get_team_users(team_id: int, current_user=fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return team_service.get_team_users_service(data_base, team_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.get("/api/team/{team_id}/projects", response_model=list[project_schemas.ProjectResponse])
def get_projects(team_id: int, current_user=fastapi.Depends(auth.get_current_user),
                 data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return project_service.get_team_projects_service(data_base, team_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.delete("/api/team/{team_id}/relation/{relation_id}", status_code=204)
def delete_task_relation(relation_id: int, current_user=fastapi.Depends(auth.get_current_user),
                         data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        task_service.delete_task_relation_service(data_base, relation_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))



@router.post("/api/team/{team_id}/project/new", response_model=project_schemas.ProjectResponse, status_code=201)
def create_project(team_id: int, project_data: project_schemas.ProjectCreate,
                   current_user=fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return project_service.create_project_service(data_base, team_id, current_user.id, project_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))
