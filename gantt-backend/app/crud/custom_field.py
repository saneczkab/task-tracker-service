from sqlalchemy.orm import Session

from app.models import custom_field as custom_field_model
from app.schemas import custom_field as custom_field_schema


def get_custom_field_by_team_and_name(db: Session, team_id: int, name: str):
    return (
        db.query(custom_field_model.CustomField)
        .filter(
            custom_field_model.CustomField.team_id == team_id,
            custom_field_model.CustomField.name == name,
        )
        .first()
    )


def create_custom_field(db: Session, team_id: int, field: custom_field_schema.CustomFieldBase):
    db_field = custom_field_model.CustomField(**field.model_dump(), team_id=team_id)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field


def get_custom_fields_by_team(db: Session, team_id: int):
    return db.query(custom_field_model.CustomField).filter(custom_field_model.CustomField.team_id == team_id).all()


def update_custom_field(db: Session, field_id: int, field_update: custom_field_schema.CustomFieldBase):
    db_field = db.query(custom_field_model.CustomField).filter(custom_field_model.CustomField.id == field_id).first()
    if db_field:
        update_data = field_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_field, key, value)
        db.commit()
        db.refresh(db_field)
    return db_field


def delete_custom_field(db: Session, field_id: int):
    db_field = db.query(custom_field_model.CustomField).filter(custom_field_model.CustomField.id == field_id).first()
    if db_field:
        db.delete(db_field)
        db.commit()
    return db_field


def set_task_custom_field_value(db: Session, task_id: int, field_value: custom_field_schema.TaskCustomFieldValueBase):
    db_value = db.query(custom_field_model.TaskCustomFieldValue).filter_by(task_id=task_id,
                                                                           custom_field_id=field_value.custom_field_id).first()

    if db_value:
        update_data = field_value.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_value, key, value)
    else:
        db_value = custom_field_model.TaskCustomFieldValue(task_id=task_id, **field_value.model_dump())
        db.add(db_value)

    db.commit()
    db.refresh(db_value)
    return db_value


def delete_task_custom_field_value(db: Session, task_id: int, custom_field_id: int):
    """Удалить значение кастомного поля для задачи."""
    db_value = db.query(custom_field_model.TaskCustomFieldValue).filter_by(
        task_id=task_id,
        custom_field_id=custom_field_id
    ).first()
    if db_value:
        db.delete(db_value)
        db.commit()
    return db_value
