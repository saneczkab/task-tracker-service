import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.schemas import goal as goal_schemas
from app.services import goal_service

router = fastapi.APIRouter()


@router.patch("/api/goal/{goal_id}", response_model=goal_schemas.GoalResponse)
def update_goal(goal_id: int, goal_data: goal_schemas.GoalUpdate, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Обновить цель"""
    try:
        return goal_service.update_goal_service(data_base, goal_id, current_user.id, goal_data)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))
    except exception.ConflictError as e:
        raise fastapi.HTTPException(status_code=409, detail=str(e))


@router.delete("/api/goal/{goal_id}", status_code=204)
def delete_goal(goal_id: int, current_user=fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить цель"""
    try:
        goal_service.delete_goal_service(data_base, goal_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))
