from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.models.role import Role
from app.tests.fixtures import *  # noqa: F403


def _chainable_query_mock(first=None, all_=None, order_by_first=None):
    query = Mock()
    query.filter.return_value = query
    query.filter_by.return_value = query
    query.order_by.return_value = query

    if order_by_first is not None:
        query.first.return_value = order_by_first
    else:
        query.first.return_value = first
    if all_ is not None:
        query.all.return_value = all_
    query.delete.return_value = None

    return query


@pytest.fixture
def make_query_router():

    def _router(mapping):
        buckets = {}
        for model, value in mapping.items():
            if isinstance(value, list):
                buckets[model] = list(value)
            else:
                buckets[model] = [value]

        def _query(model):
            if model not in buckets or not buckets[model]:
                raise AssertionError(f"Неожиданный вызов db.query({model})")
            return buckets[model].pop(0)

        return _query

    return _router


@pytest.fixture
def make_query():
    return _chainable_query_mock


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
def mock_user(ids):
    return Mock(id=ids.user_id, email="user@test.com", nickname="User")


@pytest.fixture
def mock_second_user(ids):
    return Mock(id=ids.second_user_id, email="second@test.com", nickname="Second")


@pytest.fixture
def mock_team(ids):
    return Mock(id=ids.team_id, name="Team")


@pytest.fixture
def mock_project(ids, mock_team):
    project = Mock(id=ids.project_id, team_id=mock_team.id, name="Project")
    project.team = mock_team
    project.streams = []
    return project


@pytest.fixture
def mock_stream(ids, mock_project):
    stream = Mock(id=ids.stream_id, project_id=mock_project.id, name="Stream")
    stream.project = mock_project
    return stream


@pytest.fixture
def mock_task(ids, mock_stream):
    return Mock(id=ids.task_id, stream_id=mock_stream.id, name="Task")


@pytest.fixture
def mock_goal(ids, mock_stream):
    return Mock(id=ids.goal_id, stream_id=mock_stream.id, name="Goal")


@pytest.fixture
def mock_connection_type(ids):
    return Mock(id=ids.connection_id)


@pytest.fixture
def make_team_member():
    def _make_team_member(user_id, email, nickname, role_id=Role.READER):
        member = Mock(role_id=role_id)
        member.user = Mock(id=user_id, email=email, nickname=nickname)
        return member

    return _make_team_member
