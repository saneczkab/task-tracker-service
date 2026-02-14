
import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.models import user as user_models
from app.schemas import goal as goal_schemas
from app.schemas import stream as stream_schemas
from app.schemas import task as task_schemas
from app.services import goal_service, stream_service, task_service

router = fastapi.APIRouter()


@router.get("/api/stream/{stream_id}", response_model=stream_schemas.StreamResponse,
            status_code=fastapi.status.HTTP_200_OK)
def get_stream(stream_id: int, current_user: user_models.User = fastapi.Depends(auth.get_current_user),
               data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить информацию о стриме stream_id"""
    try:
        stream = stream_service.get_stream_service(data_base, stream_id, current_user.id)
        return stream
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.patch("/api/stream/{stream_id}", response_model=stream_schemas.StreamResponse,
              status_code=fastapi.status.HTTP_200_OK)
def update_stream(stream_id: int, stream_update_data: stream_schemas.StreamUpdate,
                  current_user: user_models.User = fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
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


@router.delete("/api/stream/{stream_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_stream(stream_id: int, current_user: user_models.User = fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить стрим stream_id"""
    try:
        stream_service.delete_stream_service(data_base, stream_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.get("/api/stream/{stream_id}/tasks", response_model=list[task_schemas.TaskResponse])
def get_stream_tasks(stream_id: int, current_user=fastapi.Depends(auth.get_current_user),
                     data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return task_service.get_stream_tasks_service(data_base, stream_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.get("/api/stream/{stream_id}/goals", response_model=list[goal_schemas.GoalResponse])
def get_goals(stream_id: int, current_user=fastapi.Depends(auth.get_current_user),
              data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return goal_service.get_stream_goals_service(data_base, stream_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.post("/api/stream/{stream_id}/task/new", response_model=task_schemas.TaskResponse, status_code=201)
def create_task(stream_id: int, task_data: task_schemas.TaskCreate, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return task_service.create_task_service(data_base, stream_id, current_user.id, task_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.post("/api/stream/{stream_id}/goal/new", response_model=goal_schemas.GoalResponse, status_code=201)
def create_goal(stream_id: int, goal_data: goal_schemas.GoalCreate, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return goal_service.create_goal_service(data_base, stream_id, current_user.id, goal_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(status_code=409, detail=str(e))
