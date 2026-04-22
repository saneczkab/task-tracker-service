from unittest.mock import DEFAULT, Mock, patch

import pytest

from app.core import exception
from app.models.custom_field import CustomFieldType
from app.schemas.custom_field import CustomFieldBase
from app.services.custom_field_service import (
    create_custom_field_service,
    delete_custom_field_service,
    get_custom_fields_by_team_service,
    update_custom_field_service,
)


@patch.multiple(
    "app.services.custom_field_service.custom_field_crud",
    create_custom_field=DEFAULT,
    get_custom_field_by_team_and_name=DEFAULT,
)
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_create_custom_field_service_returns_existing_field(
    mock_check_team_access, mock_db, ids, team_obj, custom_field_obj, **mocks
):
    field_data = CustomFieldBase(name="Severity", type=CustomFieldType.STRING)
    existing_field = Mock(
        id=custom_field_obj.id,
        team_id=team_obj.id,
        name=field_data.name,
        type=field_data.type,
    )
    mocks["get_custom_field_by_team_and_name"].return_value = existing_field

    result = create_custom_field_service(mock_db, team_obj.id, ids.user_id, field_data)

    mock_check_team_access.assert_called_once_with(
        mock_db, team_obj.id, ids.user_id, need_lead=True
    )
    mocks["get_custom_field_by_team_and_name"].assert_called_once_with(
        db=mock_db,
        team_id=team_obj.id,
        name=field_data.name,
    )
    mocks["create_custom_field"].assert_not_called()
    assert result is existing_field


@patch.multiple(
    "app.services.custom_field_service.custom_field_crud",
    create_custom_field=DEFAULT,
    get_custom_field_by_team_and_name=DEFAULT,
)
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_create_custom_field_service_creates_new_field(
    mock_check_team_access, mock_db, ids, team_obj, **mocks
):
    field_data = CustomFieldBase(name="Severity", type=CustomFieldType.STRING)
    created_field = Mock(
        id=ids.goal_id,
        team_id=team_obj.id,
        name=field_data.name,
        type=field_data.type,
    )
    mocks["get_custom_field_by_team_and_name"].return_value = None
    mocks["create_custom_field"].return_value = created_field

    result = create_custom_field_service(mock_db, team_obj.id, ids.user_id, field_data)

    mock_check_team_access.assert_called_once_with(
        mock_db, team_obj.id, ids.user_id, need_lead=True
    )
    mocks["get_custom_field_by_team_and_name"].assert_called_once_with(
        db=mock_db,
        team_id=team_obj.id,
        name=field_data.name,
    )
    mocks["create_custom_field"].assert_called_once_with(
        db=mock_db,
        team_id=team_obj.id,
        field=field_data,
    )
    assert result is created_field


@patch.multiple(
    "app.services.custom_field_service.custom_field_crud",
    create_custom_field=DEFAULT,
    get_custom_field_by_team_and_name=DEFAULT,
)
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_create_custom_field_service_forbidden(
    mock_check_team_access, mock_db, team_obj, **mocks
):
    field_data = CustomFieldBase(name="Severity", type=CustomFieldType.STRING)
    mock_check_team_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        create_custom_field_service(mock_db, team_obj.id, 999, field_data)

    mocks["get_custom_field_by_team_and_name"].assert_not_called()
    mocks["create_custom_field"].assert_not_called()


@patch("app.services.custom_field_service.custom_field_crud.get_custom_fields_by_team")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_get_custom_fields_by_team_service_success(
    mock_check_team_access,
    mock_get_custom_fields_by_team,
    mock_db,
    team_obj,
    custom_field_obj,
):
    mock_get_custom_fields_by_team.return_value = [custom_field_obj]

    result = get_custom_fields_by_team_service(mock_db, team_obj.id, 999)

    mock_check_team_access.assert_called_once_with(mock_db, team_obj.id, 999)
    mock_get_custom_fields_by_team.assert_called_once_with(
        db=mock_db, team_id=team_obj.id
    )
    assert result == [custom_field_obj]


@patch("app.services.custom_field_service.custom_field_crud.update_custom_field")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_update_custom_field_service_success(
    mock_check_team_access,
    mock_update_custom_field,
    mock_db,
    team_obj,
    custom_field_obj,
):
    field_update = CustomFieldBase(name="Severity", type=CustomFieldType.TEXT)
    db_field = Mock(id=custom_field_obj.id, team_id=team_obj.id)
    mock_db.query.return_value.filter.return_value.first.return_value = db_field
    mock_update_custom_field.return_value = custom_field_obj

    result = update_custom_field_service(
        mock_db, custom_field_obj.id, 999, field_update
    )

    mock_check_team_access.assert_called_once_with(
        mock_db, team_obj.id, 999, need_lead=True
    )
    mock_update_custom_field.assert_called_once_with(
        db=mock_db,
        field_id=custom_field_obj.id,
        field_update=field_update,
    )
    assert result is custom_field_obj


@patch("app.services.custom_field_service.custom_field_crud.update_custom_field")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_update_custom_field_service_not_found(
    mock_check_team_access, mock_update_custom_field, mock_db
):
    field_update = CustomFieldBase(name="Severity", type=CustomFieldType.TEXT)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        update_custom_field_service(mock_db, 999, 999, field_update)

    mock_check_team_access.assert_not_called()
    mock_update_custom_field.assert_not_called()


@patch("app.services.custom_field_service.custom_field_crud.update_custom_field")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_update_custom_field_service_forbidden(
    mock_check_team_access,
    mock_update_custom_field,
    mock_db,
    team_obj,
    custom_field_obj,
):
    field_update = CustomFieldBase(name="Severity", type=CustomFieldType.TEXT)
    db_field = Mock(id=custom_field_obj.id, team_id=team_obj.id)
    mock_db.query.return_value.filter.return_value.first.return_value = db_field
    mock_check_team_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        update_custom_field_service(mock_db, custom_field_obj.id, 999, field_update)

    mock_update_custom_field.assert_not_called()


@patch("app.services.custom_field_service.custom_field_crud.delete_custom_field")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_delete_custom_field_service_success(
    mock_check_team_access,
    mock_delete_custom_field,
    mock_db,
    team_obj,
    custom_field_obj,
):
    db_field = Mock(id=custom_field_obj.id, team_id=team_obj.id)
    mock_db.query.return_value.filter.return_value.first.return_value = db_field
    mock_delete_custom_field.return_value = custom_field_obj

    result = delete_custom_field_service(mock_db, custom_field_obj.id, 999)

    mock_check_team_access.assert_called_once_with(
        mock_db, team_obj.id, 999, need_lead=True
    )
    mock_delete_custom_field.assert_called_once_with(
        db=mock_db, field_id=custom_field_obj.id
    )
    assert result is custom_field_obj


@patch("app.services.custom_field_service.custom_field_crud.delete_custom_field")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_delete_custom_field_service_not_found(
    mock_check_team_access, mock_delete_custom_field, mock_db
):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(exception.NotFoundError):
        delete_custom_field_service(mock_db, 999, 999)

    mock_check_team_access.assert_not_called()
    mock_delete_custom_field.assert_not_called()


@patch("app.services.custom_field_service.custom_field_crud.delete_custom_field")
@patch("app.services.custom_field_service.permissions.check_team_access")
def test_delete_custom_field_service_forbidden(
    mock_check_team_access,
    mock_delete_custom_field,
    mock_db,
    team_obj,
    custom_field_obj,
):
    db_field = Mock(id=custom_field_obj.id, team_id=team_obj.id)
    mock_db.query.return_value.filter.return_value.first.return_value = db_field
    mock_check_team_access.side_effect = exception.ForbiddenError()

    with pytest.raises(exception.ForbiddenError):
        delete_custom_field_service(mock_db, custom_field_obj.id, 999)

    mock_delete_custom_field.assert_not_called()
