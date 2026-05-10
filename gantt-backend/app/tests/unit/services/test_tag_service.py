from unittest.mock import Mock, patch

import pytest

from app.core import exception
from app.services.tag_service import (
    create_tag_service,
    delete_tag_service,
    get_team_tags_service,
)


@patch("app.services.tag_service.tag_crud.create_tag")
@patch("app.services.tag_service.permissions.check_team_access")
def test_create_tag_service_success(
    mock_check_team_access, mock_create_tag, mock_db, ids
):
    tag_data = Mock(name="Backend", color="#3B82F6")
    expected_tag = Mock(id=1)
    mock_create_tag.return_value = expected_tag

    result = create_tag_service(mock_db, ids.team_id, ids.user_id, tag_data)

    mock_check_team_access.assert_called_once_with(mock_db, ids.team_id, ids.user_id)
    mock_create_tag.assert_called_once_with(
        mock_db, ids.team_id, tag_data.name, tag_data.color
    )
    assert result is expected_tag


@patch("app.services.tag_service.tag_crud.get_team_tags")
@patch("app.services.tag_service.permissions.check_team_access")
def test_get_team_tags_service_success(
    mock_check_team_access, mock_get_team_tags, mock_db, ids
):
    expected_tags = [Mock(id=1), Mock(id=2)]
    mock_get_team_tags.return_value = expected_tags

    result = get_team_tags_service(mock_db, ids.team_id, ids.user_id)

    mock_check_team_access.assert_called_once_with(mock_db, ids.team_id, ids.user_id)
    mock_get_team_tags.assert_called_once_with(mock_db, ids.team_id)
    assert result is expected_tags


@patch("app.services.tag_service.tag_crud.delete_tag")
@patch("app.services.tag_service.tag_crud.get_tag_by_id")
@patch("app.services.tag_service.permissions.check_team_access")
def test_delete_tag_service_success(
    mock_check_team_access, mock_get_tag_by_id, mock_delete_tag, mock_db, ids
):
    tag_obj = Mock(id=1, team_id=ids.team_id)
    mock_get_tag_by_id.return_value = tag_obj

    delete_tag_service(mock_db, tag_obj.id, ids.user_id)

    mock_get_tag_by_id.assert_called_once_with(mock_db, tag_obj.id)
    mock_check_team_access.assert_called_once_with(
        mock_db, tag_obj.team_id, ids.user_id
    )
    mock_delete_tag.assert_called_once_with(mock_db, tag_obj)


@patch("app.services.tag_service.tag_crud.get_tag_by_id")
def test_delete_tag_service_not_found(mock_get_tag_by_id, mock_db, ids):
    mock_get_tag_by_id.return_value = None

    with pytest.raises(exception.NotFoundError, match="Тег не найден"):
        delete_tag_service(mock_db, ids.task_id, ids.user_id)

    mock_get_tag_by_id.assert_called_once_with(mock_db, ids.task_id)
