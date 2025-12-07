import fastapi
from sqlalchemy import orm
from app.api import auth
from app.core import db
from app.core import exception
from app.models import user
from app.schemas import user as user_schemas
from app.services import user_service

router = fastapi.APIRouter()


@router.get("/api/user_by_token", response_model=user_schemas.UserResponse, status_code=fastapi.status.HTTP_200_OK)
def get_user_by_token(current_user=fastapi.Depends(auth.get_current_user),
                      data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        user_obj, teams = user_service.get_user_by_token_service(data_base, current_user.id)

        return {
            "id": user_obj.id,
            "email": user_obj.email,
            "nickname": user_obj.nickname,
            "teams": [{"id": t.id, "name": t.name} for t in teams]
        }
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))


@router.get("/api/user/{user_id}", response_model=user_schemas.UserResponse, status_code=fastapi.status.HTTP_200_OK)
def get_user(user_id: int, current_user=fastapi.Depends(auth.get_current_user),
             data_base: orm.Session = fastapi.Depends(db.get_db)):
    try:
        user_obj, teams = user_service.get_user_service(data_base, user_id, current_user.id)

        return {
            "id": user_obj.id,
            "email": user_obj.email,
            "nickname": user_obj.nickname,
            "teams": [{"id": t.id, "name": t.name} for t in teams]
        }
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))


@router.patch("/api/user/{user_id}")
def update_user(user_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о пользователе user_id"""
    pass


@router.delete("/api/user/{user_id}")
def delete_user(user_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить юзер user_id"""
    pass
