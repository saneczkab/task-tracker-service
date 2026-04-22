from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.models.role import Role
from app.tests.fixtures import *  # noqa: F403


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def ids():
    return SimpleNamespace(
        user_id=42,
        second_user_id=43,
        team_id=44,
        project_id=45,
        stream_id=46,
        task_id=47,
        goal_id=48,
        connection_id=49,
    )


@pytest.fixture
def make_team_member():
    def _make_team_member(user_id, email, nickname, role_id=Role.READER):
        member = Mock(role_id=role_id)
        member.user = Mock(id=user_id, email=email, nickname=nickname)
        return member

    return _make_team_member
