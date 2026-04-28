import pytest
from pydantic import ValidationError

from app.schemas.team import UserWithRoleResponse
from app.schemas.user import UserResponse


def test_user_with_role_response_invalid_email():
    with pytest.raises(ValidationError):
        UserWithRoleResponse(id=1, email="not-an-email", nickname="test", role="Reader")


def test_user_with_role_response_invalid_role():
    with pytest.raises(ValidationError):
        UserWithRoleResponse(id=1, email="test@test.com", nickname="test", role="Admin")


def test_user_response_invalid_email():
    with pytest.raises(ValidationError):
        UserResponse(id=1, email="not-an-email", nickname="test", teams=[])
