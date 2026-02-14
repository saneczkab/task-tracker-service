
import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.models import user as user_models
from app.schemas import project as project_schemas
from app.schemas import stream as stream_schemas
from app.schemas import task as task_schemas
from app.services import project_service, stream_service, task_service

router = fastapi.APIRouter()


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


@router.get("/api/project/{project_id}/tasks", response_model=list[task_schemas.TaskResponse])
def get_project_tasks(project_id: int, current_user=fastapi.Depends(auth.get_current_user),
                      data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return task_service.get_project_tasks_service(data_base, project_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.get("/api/project/{proj_id}/streams", response_model=list[stream_schemas.StreamResponse],
            status_code=fastapi.status.HTTP_200_OK)
def get_project_streams(
        proj_id: int,
        current_user: user_models.User = fastapi.Depends(auth.get_current_user),
        data_base: orm.Session = fastapi.Depends(db.get_db)
):
    """Получить все стримы в проекте proj_id"""
    try:
        streams = stream_service.get_project_streams_service(data_base, proj_id, current_user.id)
        return streams
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.post("/api/project/{proj_id}/stream/new", response_model=stream_schemas.StreamResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
def create_stream(proj_id: int, stream_data: stream_schemas.StreamCreate,
                  current_user: user_models.User = fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Создать новый стрим в проекте proj_id"""
    try:
        new_stream = stream_service.create_stream_service(data_base, proj_id, stream_data, current_user.id)
        return new_stream
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(status_code=409, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))
