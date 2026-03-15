from sqlalchemy import orm

from app.core import exception
from app.crud import custom_field as custom_field_crud
from app.models import custom_field as custom_field_model
from app.schemas import custom_field as custom_field_schema
from app.services import permissions


def create_custom_field_service(data_base: orm.Session, team_id: int, user_id: int,
                                field_data: custom_field_schema.CustomFieldBase):
    permissions.check_team_access(data_base, team_id, user_id, need_lead=True)
    return custom_field_crud.create_custom_field(db=data_base, team_id=team_id, field=field_data)


def get_custom_fields_by_team_service(data_base: orm.Session, team_id: int, user_id: int):
    permissions.check_team_access(data_base, team_id, user_id)
    return custom_field_crud.get_custom_fields_by_team(db=data_base, team_id=team_id)


def update_custom_field_service(data_base: orm.Session, field_id: int, user_id: int,
                                field_update: custom_field_schema.CustomFieldBase):
    db_field = data_base.query(custom_field_model.CustomField).filter(
        custom_field_model.CustomField.id == field_id).first()
    if not db_field:
        raise exception.NotFoundError("Кастомное поле не найдено")
    permissions.check_team_access(data_base, db_field.team_id, user_id, need_lead=True)
    return custom_field_crud.update_custom_field(db=data_base, field_id=field_id, field_update=field_update)


def delete_custom_field_service(data_base: orm.Session, field_id: int, user_id: int):
    db_field = data_base.query(custom_field_model.CustomField).filter(
        custom_field_model.CustomField.id == field_id).first()
    if not db_field:
        raise exception.NotFoundError("Кастомное поле не найдено")
    permissions.check_team_access(data_base, db_field.team_id, user_id, need_lead=True)
    return custom_field_crud.delete_custom_field(db=data_base, field_id=field_id)
