import typing
import fastapi
from sqlalchemy import orm
from app.core import db, exception
from app.services import stream_service
from app.schemas import stream as stream_schemas
from app.api import auth
from app.models import user as user_models


router = fastapi.APIRouter()


@router.get("/api/project/{proj_id}/streams",
            response_model=typing.List[stream_schemas.StreamResponse],
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


@router.get("/api/stream/{stream_id}",
            response_model=stream_schemas.StreamResponse,
            status_code=fastapi.status.HTTP_200_OK)
def get_stream(
    stream_id: int,
    current_user: user_models.User = fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db)
):
    """Получить информацию о стриме stream_id"""
    try:
        stream = stream_service.get_stream_service(data_base, stream_id, current_user.id)
        return stream
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.post("/api/project/{proj_id}/stream/new",
             response_model=stream_schemas.StreamResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
def create_stream(
    proj_id: int,
    stream_data: stream_schemas.StreamCreate,
    current_user: user_models.User = fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db)
):
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


@router.patch("/api/stream/{stream_id}",
              response_model=stream_schemas.StreamResponse,
              status_code=fastapi.status.HTTP_200_OK)
def update_stream(
    stream_id: int,
    stream_update_data: stream_schemas.StreamUpdate,
    current_user: user_models.User = fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db)
):
    """Частично обновить данные о стриме stream_id"""
    try:
        updated_stream = stream_service.update_stream_service(data_base, stream_id, stream_update_data, current_user.id)
        return updated_stream
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(status_code=409, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.delete("/api/stream/{stream_id}",
               status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_stream(
    stream_id: int,
    current_user: user_models.User = fastapi.Depends(auth.get_current_user),
    data_base: orm.Session = fastapi.Depends(db.get_db)
):
    """Удалить стрим stream_id"""
    try:
        stream_service.delete_stream_service(data_base, stream_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))