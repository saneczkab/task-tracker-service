from unittest.mock import Mock

import fastapi
import pytest

from app.api import stream as stream_api
from app.models import stream as stream_models


class TestStream:

    def setup_mocks(self):
        self.mock_db = Mock()
        self.mock_user = Mock()
        self.mock_user.id = 10

        self.mock_user_team = Mock()
        self.mock_user_team.role_id = 2

        self.mock_project = Mock()
        self.mock_project.id = 1
        self.mock_project.team_id = 999

        self.mock_stream = Mock(spec=stream_models.Stream)
        self.mock_stream.id = 5
        self.mock_stream.project_id = 1
        self.mock_stream.name = "Backend"

    def test_get_project_streams_success(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        self.mock_db.query.return_value.filter.return_value.all.return_value = [
            self.mock_stream
        ]

        result = stream_api.get_project_streams(1, self.mock_user, self.mock_db)
        assert result == [self.mock_stream]

    def test_get_project_streams_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.get_project_streams(1, self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_get_project_streams_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.get_project_streams(1, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_get_stream_success(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        result = stream_api.get_stream(5, self.mock_user, self.mock_db)
        assert result == self.mock_stream

    def test_get_stream_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.get_stream(5, self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_get_stream_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.get_stream(5, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_create_stream_success(self, monkeypatch):
        self.setup_mocks()

        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team,
            None
        ]

        mock_stream_class = Mock()
        monkeypatch.setattr(stream_models, "Stream", mock_stream_class)

        stream_data = Mock()
        stream_data.name = "New"

        stream_api.create_stream(1, stream_data, self.mock_user, self.mock_db)

        mock_stream_class.assert_called_once_with(name="New", project_id=1)
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    def test_create_stream_project_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.create_stream(1, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_create_stream_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.create_stream(1, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_create_stream_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.create_stream(1, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_create_stream_duplicate(self):
        self.setup_mocks()

        stream_data = Mock()
        stream_data.name = "New"

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_project,
            self.mock_user_team,
            self.mock_stream
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.create_stream(1, stream_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 409

    def test_update_stream_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.update_stream(5, Mock(), self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_update_stream_no_access(self):
        self.setup_mocks()

        update_data = Mock()
        update_data.name = None

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.update_stream(5, update_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_update_stream_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        update_data = Mock()
        update_data.name = None

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.update_stream(5, update_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_update_stream_duplicate_name(self):
        self.setup_mocks()

        update_data = Mock()
        update_data.name = "Duplicate"

        self.mock_stream.name = "Old"

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team,
            self.mock_stream
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.update_stream(5, update_data, self.mock_user, self.mock_db)

        assert exc.value.status_code == 409

    def test_update_stream_success(self):
        self.setup_mocks()

        update_data = Mock()
        update_data.name = "Updated"

        self.mock_stream.name = "Old"

        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team,
            None
        ]

        result = stream_api.update_stream(5, update_data, self.mock_user, self.mock_db)

        assert result == self.mock_stream
        assert self.mock_stream.name == "Updated"

    def test_delete_stream_not_found(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.delete_stream(5, self.mock_user, self.mock_db)

        assert exc.value.status_code == 404

    def test_delete_stream_no_access(self):
        self.setup_mocks()

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.delete_stream(5, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_delete_stream_no_permission(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 1

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            stream_api.delete_stream(5, self.mock_user, self.mock_db)

        assert exc.value.status_code == 403

    def test_delete_stream_success(self):
        self.setup_mocks()

        self.mock_user_team.role_id = 2

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_stream,
            self.mock_project,
            self.mock_user_team
        ]

        result = stream_api.delete_stream(5, self.mock_user, self.mock_db)

        assert result is None
        self.mock_db.delete.assert_called_once_with(self.mock_stream)
        self.mock_db.commit.assert_called_once()
