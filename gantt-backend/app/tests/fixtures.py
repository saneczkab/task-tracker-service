import os

os.environ["AUTH_SECRET_KEY"] = "test-secret-key"
os.environ["AUTH_DATABASE_URL"] = "sqlite://"
os.environ["AUTH_VAPID_PRIVATE_KEY"] = "test-vapid-key"
os.environ["AUTH_VAPID_CLAIMS_SUB"] = "https://gantt-tracker.ru"

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import get_db
from app.core.security import create_access_token, get_password_hash
from app.models import goal as goal_model
from app.models import meta as meta_model
from app.models import project as project_model
from app.models import stream as stream_model
from app.models import task as task_model
from app.models import team as team_model
from app.models import user as user_model
from app.models.base import Base
from app.tests.factories import (
    build_connection_type,
    build_goal,
    build_priority,
    build_project,
    build_status,
    build_stream,
    build_task,
    build_team,
    build_user,
)

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=_engine)
_SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=_engine,
)

with (
    patch("app.core.db.engine", _engine),
    patch("app.core.db.SessionLocal", _SessionLocal),
):
    from main import app


def _persist(db_session, obj):
    db_session.add(obj)
    db_session.commit()
    return obj


@pytest.fixture(scope="function")
def db_session():
    connection = _engine.connect()
    transaction = connection.begin()
    session = _SessionLocal(bind=connection)
    yield session
    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "42"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def role_editor():
    return team_model.Role(id=2, name="Editor")


@pytest.fixture
def current_user():
    return build_user()


@pytest.fixture
def team():
    return build_team()


@pytest.fixture
def user_with_role():
    user = build_user(nickname="Test user")
    user.role = "Reader"
    return user


@pytest.fixture
def project():
    return build_project()


@pytest.fixture
def stream():
    return build_stream()


@pytest.fixture
def task():
    return build_task()


@pytest.fixture
def goal():
    return build_goal()


@pytest.fixture
def relation():
    relation_obj = task_model.TaskRelation(
        id=42, task_id_1=42, task_id_2=43, connection_id=42
    )
    relation_obj.connection = build_connection_type()
    return relation_obj


@pytest.fixture
def status():
    return build_status()


@pytest.fixture
def priority():
    return build_priority()


@pytest.fixture
def connection():
    return build_connection_type()


@pytest.fixture
def user_obj(db_session):
    return _persist(
        db_session,
        user_model.User(
            id=42,
            email="test@test.com",
            nickname="test_nick",
            password_hash="hash",
        ),
    )


@pytest.fixture
def second_user_obj(db_session):
    return _persist(
        db_session,
        user_model.User(
            id=43,
            email="second@test.com",
            nickname="second_nick",
            password_hash="hash",
        ),
    )


@pytest.fixture
def team_obj(db_session):
    return _persist(db_session, team_model.Team(id=42, name="Test team"))


@pytest.fixture
def user_team_obj(db_session, role_editor, user_obj, team_obj):
    return _persist(
        db_session,
        team_model.UserTeam(
            id=42,
            user_id=user_obj.id,
            team_id=team_obj.id,
            role_id=role_editor.id,
        ),
    )


@pytest.fixture
def project_obj(db_session, team_obj):
    return _persist(
        db_session,
        project_model.Project(id=42, name="Test project", team_id=team_obj.id),
    )


@pytest.fixture
def stream_obj(db_session, project_obj):
    return _persist(
        db_session,
        stream_model.Stream(id=42, name="Test stream", project_id=project_obj.id),
    )


@pytest.fixture
def second_stream_obj(db_session, project_obj):
    return _persist(
        db_session,
        stream_model.Stream(id=43, name="Second stream", project_id=project_obj.id),
    )


@pytest.fixture
def goal_obj(db_session):
    existing = (
        db_session.query(goal_model.Goal).filter(goal_model.Goal.id == 42).first()
    )
    if existing:
        return existing

    stream = (
        db_session.query(stream_model.Stream)
        .filter(stream_model.Stream.id == 42)
        .first()
    )
    if stream is None:
        team = (
            db_session.query(team_model.Team).filter(team_model.Team.id == 42).first()
        )
        if team is None:
            team = _persist(db_session, team_model.Team(id=42, name="Test team"))

        project = (
            db_session.query(project_model.Project)
            .filter(project_model.Project.id == 42)
            .first()
        )
        if project is None:
            project = _persist(
                db_session,
                project_model.Project(id=42, name="Test project", team_id=team.id),
            )

        stream = _persist(
            db_session,
            stream_model.Stream(id=42, name="Test stream", project_id=project.id),
        )

    return _persist(
        db_session,
        goal_model.Goal(
            id=42,
            name="Test",
            description=None,
            start_date=None,
            deadline=build_goal().deadline,
            stream_id=stream.id,
            position=1,
        ),
    )


@pytest.fixture
def task_obj(db_session, stream_obj):
    return _persist(
        db_session,
        task_model.Task(
            id=42,
            stream_id=stream_obj.id,
            name="Test task",
            description=None,
            status_id=None,
            priority_id=None,
            start_date=None,
            deadline=None,
            position=1,
        ),
    )


@pytest.fixture
def status_obj(db_session):
    return _persist(db_session, meta_model.Status(id=42, name="To Do"))


@pytest.fixture
def priority_obj(db_session):
    return _persist(db_session, meta_model.Priority(id=42, name="Low"))


@pytest.fixture
def connection_type_obj(db_session):
    return _persist(db_session, meta_model.ConnectionType(id=1, name="FS"))


@pytest.fixture
def seed_db(db_session):
    _persist(db_session, team_model.Role(id=2, name="Editor"))
    test_user = _persist(
        db_session,
        user_model.User(
            id=42,
            email="test@test.com",
            nickname="test_user",
            password_hash=get_password_hash("password"),
        ),
    )
    test_team = _persist(db_session, team_model.Team(id=42, name="Test team"))
    _persist(
        db_session,
        team_model.UserTeam(
            id=42, user_id=test_user.id, team_id=test_team.id, role_id=2
        ),
    )
    test_project = _persist(
        db_session,
        project_model.Project(id=42, name="Test project", team_id=test_team.id),
    )
    _persist(
        db_session,
        stream_model.Stream(id=42, name="Test stream", project_id=test_project.id),
    )
    return db_session
