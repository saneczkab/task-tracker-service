from unittest.mock import Mock

import fastapi
import pytest

from app.api import team as team_api
from app.models import team as team_model


class TestTeam:

    def setup_mocks(self):
        self.db = Mock()
        self.current_user = Mock()
        self.current_user.id = 10

        self.mock_team = Mock()
        self.mock_user_team = Mock()
        self.mock_user_team.role_id = 2

        self.mock_user = Mock()
        self.mock_user.id = 50
        self.mock_user.email = "test@example.com"
        self.mock_user.nickname = "nickname"

    def test_get_team_users_success(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        member = Mock()
        member.user = self.mock_user
        member.role_id = 2
        self.db.query.return_value.filter.return_value.all.return_value = [member]

        result = team_api.get_team_users(1, self.current_user, self.db)

        assert len(result) == 1
        assert result[0].email == "test@example.com"

    def test_get_team_users_not_found(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.get_team_users(1, self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_get_team_users_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.get_team_users(1, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_create_team_success(self, monkeypatch):
        self.setup_mocks()

        team_data = Mock()
        team_data.name = "New"

        mock_team_class = Mock()
        monkeypatch.setattr(team_model, "Team", mock_team_class)

        mock_user_team_class = Mock()
        monkeypatch.setattr(team_model, "UserTeam", mock_user_team_class)

        team_api.create_team(team_data, self.current_user, self.db)

        mock_team_class.assert_called_once()
        mock_user_team_class.assert_called_once()
        self.db.add.assert_called()
        self.db.commit.assert_called_once()

    def test_update_team_not_found(self):
        self.setup_mocks()
        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.update_team(1, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_update_team_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.update_team(1, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_update_team_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.update_team(1, Mock(), self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_update_team_success(self):
        self.setup_mocks()

        update_data = Mock()
        update_data.name = "new"
        update_data.newUsers = None
        update_data.deleteUsers = None

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        result = team_api.update_team(1, update_data, self.current_user, self.db)

        assert result == self.mock_team
        assert self.mock_team.name == "new"
        self.db.commit.assert_called_once()

    def test_delete_team_not_found(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.delete_team(1, self.current_user, self.db)

        assert exc.value.status_code == 404

    def test_delete_team_no_access(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            None
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.delete_team(1, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_delete_team_no_permission(self):
        self.setup_mocks()
        self.mock_user_team.role_id = 1

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        with pytest.raises(fastapi.HTTPException) as exc:
            team_api.delete_team(1, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_delete_team_success(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team,
            self.mock_user_team
        ]

        self.db.query.return_value.filter.return_value.all.return_value = []

        result = team_api.delete_team(1, self.current_user, self.db)

        assert result is None
        self.db.commit.assert_called_once()
