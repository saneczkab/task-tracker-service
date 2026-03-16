import os

os.environ.setdefault("AUTH_SECRET_KEY", "test-secret-key")
os.environ.setdefault("AUTH_DATABASE_URL", "sqlite://")
os.environ.setdefault("AUTH_VAPID_PRIVATE_KEY", "test-vapid-key")
os.environ.setdefault("AUTH_VAPID_CLAIMS_SUB", "https://gantt-tracker.ru")

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import get_db
from app.core.security import create_access_token, get_password_hash
from app.models import project, stream, team, user
from app.models.base import Base

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=_engine)

with (
    patch("app.core.db.engine", _engine),
    patch(
        "app.core.db.SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=_engine),
    ),
):
    from main import app


@pytest.fixture(scope="function")
def db_session():
    connection = _engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_db(db_session):
    role_editor = team.Role(id=2, name="Editor")
    db_session.add(role_editor)

    test_user = user.User(
        id=42,
        email="test@test.com",
        nickname="test_user",
        password_hash=get_password_hash("password"),
    )
    db_session.add(test_user)

    test_team = team.Team(id=42, name="Test team")
    db_session.add(test_team)

    user_team = team.UserTeam(id=42, user_id=42, team_id=42, role_id=2)
    db_session.add(user_team)

    test_project = project.Project(id=42, name="Test project", team_id=42)
    db_session.add(test_project)

    test_stream = stream.Stream(id=42, name="Test stream", project_id=42)
    db_session.add(test_stream)

    db_session.commit()
    return db_session


@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "42"})
    return {"Authorization": f"Bearer {token}"}
