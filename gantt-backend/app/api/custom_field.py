import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db, exception
from app.schemas import custom_field as custom_field_schema
from app.services import custom_field_service

router = fastapi.APIRouter()


@router.post("/api/teams/{team_id}/custom_fields/", response_model=custom_field_schema.CustomField)
def create_custom_field(team_id: int, field: custom_field_schema.CustomFieldBase,
                        current_user=fastapi.Depends(auth.get_current_user),
                        data_base: orm.Session = fastapi.Depends(db.get_db), ):
    """Создать кастомное поле для команды."""
    try:
        return custom_field_service.create_custom_field_service(data_base, team_id, current_user.id, field)
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.get("/api/teams/{team_id}/custom_fields/", response_model=list[custom_field_schema.CustomField])
def read_custom_fields(team_id: int, current_user=fastapi.Depends(auth.get_current_user),
                       data_base: orm.Session = fastapi.Depends(db.get_db), ):
    """Получить список кастомных полей для команды."""
    try:
        return custom_field_service.get_custom_fields_by_team_service(data_base, team_id, current_user.id)
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.put("/api/custom_fields/{field_id}/", response_model=custom_field_schema.CustomField)
def update_custom_field(field_id: int, field: custom_field_schema.CustomFieldBase,
                        current_user=fastapi.Depends(auth.get_current_user),
                        data_base: orm.Session = fastapi.Depends(db.get_db), ):
    """Обновить кастомное поле."""
    try:
        return custom_field_service.update_custom_field_service(data_base, field_id, current_user.id, field)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))


@router.delete("/api/custom_fields/{field_id}/", response_model=custom_field_schema.CustomField)
def delete_custom_field(field_id: int, current_user=fastapi.Depends(auth.get_current_user),
                        data_base: orm.Session = fastapi.Depends(db.get_db), ):
    """Удалить кастомное поле."""
    try:
        return custom_field_service.delete_custom_field_service(data_base, field_id, current_user.id)
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(status_code=403, detail=str(e))
