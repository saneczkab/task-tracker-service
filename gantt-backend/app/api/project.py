import fastapi
from sqlalchemy import orm

from app.core import db
from app.api import auth
from app.core import exception
from app.schemas import project as project_schemas
from app.services import project_service

router = fastapi.APIRouter()


@router.get("/api/team/{team_id}/projects", response_model=list[project_schemas.ProjectResponse])
def get_projects(team_id: int, current_user=fastapi.Depends(auth.get_current_user),
                 data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return project_service.get_team_projects_service(data_base, team_id, current_user.id)
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


@router.patch("/api/project/{proj_id}", response_model=project_schemas.ProjectResponse)
def update_project(proj_id: int, update_data: project_schemas.ProjectUpdate,
                   current_user=fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return project_service.update_project_service(data_base, proj_id, current_user.id, update_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.delete("/api/project/{proj_id}", status_code=204)
def delete_project(proj_id: int, current_user=fastapi.Depends(auth.get_current_user),
                   data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        project_service.delete_project_service(data_base, proj_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))
