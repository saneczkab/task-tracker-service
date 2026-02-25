import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.schemas import task as task_schemas
from app.services import task_service

router = fastapi.APIRouter()


@router.get("/api/tasks/all", response_model=list[task_schemas.TaskResponseFull],
            status_code=fastapi.status.HTTP_200_OK)
def get_all_tasks(current_user=fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все задачи пользователя"""
    return task_service.get_all_tasks_service(data_base, current_user.id)


@router.patch("/api/task/{task_id}", response_model=task_schemas.TaskResponse)
def update_task(task_id: int, task_data: task_schemas.TaskUpdate, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return task_service.update_task_service(data_base, task_id, current_user.id, task_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.delete("/api/task/{task_id}", status_code=204)
def delete_task(task_id: int, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        task_service.delete_task_service(data_base, task_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))


@router.post("/api/task/{task_id}/relation", response_model=task_schemas.TaskRelationResponse)
def create_task_relation(task_id: int, data: task_schemas.TaskRelationCreate,
                         data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        return task_service.create_task_relation_service(data_base, task_id, data.task_id, data.connection_id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(400, str(e))
