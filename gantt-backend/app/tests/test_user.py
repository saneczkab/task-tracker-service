from unittest.mock import Mock

import fastapi
import pytest

from app.api import user as user_api


class TestUser:

    def setup_mocks(self):
        self.db = Mock()
        self.current_user = Mock()
        self.current_user.id = 10
        self.current_user.email = "test@example.com"
        self.current_user.nickname = "test"

        self.mock_user = Mock()
        self.mock_user.id = 10
        self.mock_user.email = "test@example.com"
        self.mock_user.nickname = "test"

        self.mock_team = Mock()
        self.mock_team.id = 1
        self.mock_team.name = "team 1"

        self.mock_user_team = Mock()
        self.mock_user_team.team = self.mock_team

    def test_get_user_by_token_success(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.all.return_value = [
            self.mock_user_team
        ]

        result = user_api.get_user_by_token(self.current_user, self.db)

        assert result["id"] == 10
        assert result["email"] == "test@example.com"
        assert len(result["teams"]) == 1
        assert result["teams"][0]["name"] == "team 1"

    def test_get_user_success(self):
        self.setup_mocks()

        self.db.query.return_value.filter.return_value.first.return_value = self.mock_user
        self.db.query.return_value.filter.return_value.all.return_value = [
            self.mock_user_team
        ]

        result = user_api.get_user(10, self.current_user, self.db)

        assert result["id"] == 10
        assert result["email"] == "test@example.com"

    def test_get_user_forbidden(self):
        self.setup_mocks()
        with pytest.raises(fastapi.HTTPException) as exc:
            user_api.get_user(99, self.current_user, self.db)

        assert exc.value.status_code == 403

    def test_get_user_not_found(self):
        self.setup_mocks()
        self.current_user.id = 10
        
        self.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(fastapi.HTTPException) as exc:
            user_api.get_user(10, self.current_user, self.db)

        assert exc.value.status_code == 404
