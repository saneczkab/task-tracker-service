from unittest import mock

import fastapi
import pytest
from sqlalchemy import exc

from app.api import auth


class TestAuth:

    def test_check_email_exists(self):
        mock_db = mock.Mock()
        mock_user = mock.Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = auth.check_email("test@example.com", mock_db)
        assert result == {"exists": True}

    def test_check_email_not_exists(self):
        mock_db = mock.Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = auth.check_email("nonexistent@example.com", mock_db)
        assert result == {"exists": False}

    def test_register_success(self):
        mock_db = mock.Mock()
        mock_user = mock.Mock()
        mock_user.id = 1

        with mock.patch("app.models.user.User", return_value=mock_user), mock.patch(
                "app.core.security.get_password_hash", return_value="hashed_password"), \
                mock.patch("app.core.security.create_access_token", return_value="test_token"):
            result = auth.register("new@example.com", "new_nickname", "password123", mock_db)

            assert result == {"access_token": "test_token", "token_type": "Bearer"}
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    def test_register_duplicate(self):
        mock_db = mock.Mock()
        mock_user = mock.Mock()

        mock_db.commit.side_effect = exc.IntegrityError("Mocked", "params", Exception())

        with mock.patch("app.models.user.User", return_value=mock_user):
            with pytest.raises(fastapi.HTTPException) as exc_info:
                auth.register("test@example.com", "taken_nickname", "pass123", mock_db)

        assert exc_info.value.status_code == 409
        mock_db.rollback.assert_called_once()

    def test_login_success(self):
        mock_db = mock.Mock()
        mock_user = mock.Mock()
        mock_user.password_hash = "hashed_password"
        mock_user.id = 1

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with mock.patch("app.core.security.verify_password", return_value=True), mock.patch(
                "app.core.security.create_access_token", return_value="login_token"):
            result = auth.login("test@example.com", "correct_password", mock_db)

            assert result == {"access_token": "login_token", "token_type": "Bearer"}

    def test_login_wrong_password(self):
        mock_db = mock.Mock()
        mock_user = mock.Mock()
        mock_user.password_hash = "hashed_password"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with mock.patch("app.core.security.verify_password", return_value=False):
            with pytest.raises(fastapi.HTTPException) as exc_info:
                auth.login("test@example.com", "wrong_password", mock_db)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        mock_db = mock.Mock()
        mock_user = mock.Mock()
        mock_user.id = 1

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        mock_request = mock.Mock(spec=fastapi.Request)
        mock_request.state.user_id = 1

        result = auth.get_current_user(mock_request, mock_db)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_no_user_id(self):
        mock_db = mock.Mock()

        mock_request = mock.Mock(spec=fastapi.Request)
        mock_request.state.user_id = None

        with pytest.raises(fastapi.HTTPException) as exc_info:
            auth.get_current_user(mock_request, mock_db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        mock_db = mock.Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_request = mock.Mock(spec=fastapi.Request)
        mock_request.state.user_id = 999

        with pytest.raises(fastapi.HTTPException) as exc_info:
            auth.get_current_user(mock_request, mock_db)

        assert exc_info.value.status_code == 404
