from app.crud.custom_field import (
    create_custom_field,
    delete_custom_field,
    delete_task_custom_field_value,
    get_custom_field_by_team_and_name,
    get_custom_fields_by_team,
    set_task_custom_field_value,
    update_custom_field,
)
from app.models import custom_field as custom_field_model
from app.schemas.custom_field import CustomFieldBase, TaskCustomFieldValueBase


def test_get_custom_field_by_team_and_name_returns_field(db_session, custom_field_obj):
    result = get_custom_field_by_team_and_name(
        db_session, custom_field_obj.team_id, custom_field_obj.name
    )

    assert result is not None
    assert result.id == custom_field_obj.id
    assert result.team_id == custom_field_obj.team_id
    assert result.name == custom_field_obj.name


def test_get_custom_field_by_team_and_name_returns_none_when_not_found(db_session):
    result = get_custom_field_by_team_and_name(db_session, team_id=999, name="unknown")

    assert result is None


def test_get_custom_fields_by_team_returns_list(db_session, custom_field_obj):
    second_field_data = CustomFieldBase(
        name="Priority",
        type=custom_field_model.CustomFieldType.STRING,
    )
    second_field = create_custom_field(
        db_session,
        custom_field_obj.team_id,
        second_field_data,
    )

    result = get_custom_fields_by_team(db_session, custom_field_obj.team_id)

    assert len(result) == 2
    assert {item.id for item in result} == {custom_field_obj.id, second_field.id}


def test_get_custom_fields_by_team_returns_empty_list_when_not_found(db_session):
    result = get_custom_fields_by_team(db_session, team_id=999)

    assert result == []


def test_create_custom_field_persists_field(db_session, team_obj):
    field_data = CustomFieldBase(
        name="Severity", type=custom_field_model.CustomFieldType.STRING
    )

    result = create_custom_field(db_session, team_obj.id, field_data)

    assert result.id is not None
    assert result.team_id == team_obj.id
    assert result.name == field_data.name
    assert result.type == field_data.type


def test_update_custom_field_updates_values(db_session, custom_field_obj):
    field_update = CustomFieldBase(
        name="Business value",
        type=custom_field_model.CustomFieldType.TEXT,
    )

    result = update_custom_field(db_session, custom_field_obj.id, field_update)

    assert result is not None
    assert result.id == custom_field_obj.id
    assert result.name == field_update.name
    assert result.type == field_update.type


def test_update_custom_field_returns_none_when_not_found(db_session):
    field_update = CustomFieldBase(
        name="Updated", type=custom_field_model.CustomFieldType.STRING
    )

    result = update_custom_field(db_session, field_id=999, field_update=field_update)

    assert result is None


def test_delete_custom_field_deletes_record(db_session, custom_field_obj):
    result = delete_custom_field(db_session, custom_field_obj.id)

    assert result is not None
    assert result.id == custom_field_obj.id
    assert (
        get_custom_field_by_team_and_name(
            db_session,
            custom_field_obj.team_id,
            custom_field_obj.name,
        )
        is None
    )


def test_delete_custom_field_returns_none_when_not_found(db_session):
    result = delete_custom_field(db_session, field_id=999)

    assert result is None


def test_set_task_custom_field_value_creates_value(
    db_session, task_obj, custom_field_obj
):
    value_data = TaskCustomFieldValueBase(
        custom_field_id=custom_field_obj.id,
        value_string="13",
    )

    result = set_task_custom_field_value(db_session, task_obj.id, value_data)

    assert result.id is not None
    assert result.task_id == task_obj.id
    assert result.custom_field_id == value_data.custom_field_id
    assert result.value_string == value_data.value_string


def test_set_task_custom_field_value_updates_existing_value(
    db_session,
    task_custom_field_value_obj,
):
    value_data = TaskCustomFieldValueBase(
        custom_field_id=task_custom_field_value_obj.custom_field_id,
        value_string="21",
    )

    result = set_task_custom_field_value(
        db_session,
        task_custom_field_value_obj.task_id,
        value_data,
    )

    assert result.id == task_custom_field_value_obj.id
    assert result.task_id == task_custom_field_value_obj.task_id
    assert result.custom_field_id == task_custom_field_value_obj.custom_field_id
    assert result.value_string == value_data.value_string

    values_count = (
        db_session.query(custom_field_model.TaskCustomFieldValue)
        .filter_by(
            task_id=task_custom_field_value_obj.task_id,
            custom_field_id=task_custom_field_value_obj.custom_field_id,
        )
        .count()
    )
    assert values_count == 1


def test_delete_task_custom_field_value_deletes_record(
    db_session, task_custom_field_value_obj
):
    result = delete_task_custom_field_value(
        db_session,
        task_custom_field_value_obj.task_id,
        task_custom_field_value_obj.custom_field_id,
    )

    assert result is not None
    assert result.id == task_custom_field_value_obj.id

    db_value = (
        db_session.query(custom_field_model.TaskCustomFieldValue)
        .filter_by(
            task_id=task_custom_field_value_obj.task_id,
            custom_field_id=task_custom_field_value_obj.custom_field_id,
        )
        .first()
    )
    assert db_value is None


def test_delete_task_custom_field_value_returns_none_when_not_found(
    db_session,
    task_obj,
    custom_field_obj,
):
    result = delete_task_custom_field_value(
        db_session, task_obj.id, custom_field_obj.id
    )

    assert result is None
