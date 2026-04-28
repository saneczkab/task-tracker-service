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
from app.core.security import create_access_token
from app.models import goal as goal_model
from app.models import project as project_model
from app.models import stream as stream_model
from app.models import team as team_model
from app.models.base import Base
from app.tests.factories import (
    build_connection_type,
    build_custom_field,
    build_goal,
    build_push_subscription,
    build_priority,
    build_project,
    build_reminder,
    build_role,
    build_status,
    build_stream,
    build_task,
    build_task_custom_field_value,
    build_task_relation,
    build_tag,
    build_team,
    build_user,
    build_user_team,
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
    return build_role()


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
def relation(connection):
    relation_obj = build_task_relation()
    relation_obj.connection = connection
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
        build_user(
            user_id=42,
            email="test@test.com",
        ),
    )


@pytest.fixture
def second_user_obj(db_session):
    return _persist(
        db_session,
        build_user(
            user_id=43,
            email="second@test.com",
            nickname="second_nick",
        ),
    )


@pytest.fixture
def team_obj(db_session):
    return _persist(db_session, build_team())


@pytest.fixture
def user_team_obj(db_session, role_editor, user_obj, team_obj):
    return _persist(
        db_session,
        build_user_team(
            user_id=user_obj.id,
            team_id=team_obj.id,
            role_id=role_editor.id,
        ),
    )


@pytest.fixture
def project_obj(db_session, team_obj):
    return _persist(
        db_session,
        build_project(team_id=team_obj.id),
    )


@pytest.fixture
def stream_obj(db_session, project_obj):
    return _persist(
        db_session,
        build_stream(project_id=project_obj.id),
    )


@pytest.fixture
def second_stream_obj(db_session, project_obj):
    return _persist(
        db_session,
        build_stream(stream_id=43, project_id=project_obj.id),
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
            team = _persist(db_session, build_team())

        project = (
            db_session.query(project_model.Project)
            .filter(project_model.Project.id == 42)
            .first()
        )
        if project is None:
            project = _persist(
                db_session,
                build_project(team_id=team.id),
            )

        stream = _persist(
            db_session,
            build_stream(project_id=project.id),
        )

    goal = build_goal(stream_id=stream.id)
    return _persist(db_session, goal)


@pytest.fixture
def task_obj(db_session, stream_obj):
    deadline = build_goal().deadline
    return _persist(
        db_session,
        build_task(
            stream_id=stream_obj.id,
            start_date=deadline,
            deadline=deadline,
        ),
    )


@pytest.fixture
def second_task_obj(db_session, second_stream_obj):
    deadline = build_goal().deadline
    return _persist(
        db_session,
        build_task(
            task_id=43,
            stream_id=second_stream_obj.id,
            start_date=deadline,
            deadline=deadline,
            position=2,
        ),
    )


@pytest.fixture
def push_subscription_obj(db_session, user_obj):
    return _persist(
        db_session,
        build_push_subscription(
            user_id=user_obj.id,
        ),
    )


@pytest.fixture
def second_push_subscription_obj(db_session, second_user_obj):
    return _persist(
        db_session,
        build_push_subscription(
            subscription_id=43,
            user_id=second_user_obj.id,
        ),
    )


@pytest.fixture
def reminder_obj(db_session, task_obj, user_obj):
    return _persist(
        db_session,
        build_reminder(
            task_id=task_obj.id,
            user_id=user_obj.id,
        ),
    )


@pytest.fixture
def second_reminder_obj(db_session, second_task_obj, user_obj):
    return _persist(
        db_session,
        build_reminder(
            reminder_id=43,
            task_id=second_task_obj.id,
            user_id=user_obj.id,
            sent=True,
        ),
    )


@pytest.fixture
def foreign_reminder_obj(db_session, task_obj, second_user_obj):
    return _persist(
        db_session,
        build_reminder(
            reminder_id=99,
            task_id=task_obj.id,
            user_id=second_user_obj.id,
            sent=False,
        ),
    )


@pytest.fixture
def custom_field_obj(db_session, team_obj):
    return _persist(
        db_session,
        build_custom_field(team_id=team_obj.id),
    )


@pytest.fixture
def task_custom_field_value_obj(db_session, task_obj, custom_field_obj):
    return _persist(
        db_session,
        build_task_custom_field_value(
            task_id=task_obj.id,
            custom_field_id=custom_field_obj.id,
        ),
    )


@pytest.fixture
def tag_obj(db_session, team_obj):
    return _persist(
        db_session,
        build_tag(team_id=team_obj.id),
    )


@pytest.fixture
def status_obj(db_session):
    return _persist(db_session, build_status())


@pytest.fixture
def priority_obj(db_session):
    return _persist(db_session, build_priority())


@pytest.fixture
def connection_type_obj(db_session):
    return _persist(db_session, build_connection_type())


@pytest.fixture
def other_team_obj(db_session):
    return _persist(db_session, build_team(team_id=99, name="Other team"))


@pytest.fixture
def other_project_obj(db_session, other_team_obj):
    return _persist(
        db_session,
        build_project(project_id=99, name="Other project", team_id=other_team_obj.id),
    )


@pytest.fixture
def other_stream_obj(db_session, other_project_obj):
    return _persist(
        db_session,
        build_stream(
            stream_id=99, name="Other stream", project_id=other_project_obj.id
        ),
    )


@pytest.fixture
def other_goal_obj(db_session, other_stream_obj):
    return _persist(
        db_session,
        build_goal(
            goal_id=99, name="Other goal", stream_id=other_stream_obj.id, position=1
        ),
    )


@pytest.fixture
def other_tag_obj(db_session, other_team_obj):
    return _persist(
        db_session,
        build_tag(tag_id=99, team_id=other_team_obj.id, name="Other", color="#FFFFFF"),
    )


@pytest.fixture
def other_task_1_obj(db_session, other_stream_obj):
    return _persist(
        db_session,
        build_task(
            task_id=99, name="Other task 1", stream_id=other_stream_obj.id, position=1
        ),
    )


@pytest.fixture
def other_task_2_obj(db_session, other_stream_obj):
    return _persist(
        db_session,
        build_task(
            task_id=100, name="Other task 2", stream_id=other_stream_obj.id, position=2
        ),
    )


@pytest.fixture
def other_relation_obj(
    db_session, other_task_1_obj, other_task_2_obj, connection_type_obj
):
    relation = build_task_relation(
        relation_id=99,
        task_id_1=other_task_1_obj.id,
        task_id_2=other_task_2_obj.id,
        connection_id=connection_type_obj.id,
    )
    return _persist(db_session, relation)


@pytest.fixture
def other_custom_field_obj(db_session, other_team_obj):
    return _persist(
        db_session,
        build_custom_field(field_id=99, team_id=other_team_obj.id),
    )


@pytest.fixture
def other_task_custom_field_value_obj(
    db_session, other_task_1_obj, other_custom_field_obj
):
    return _persist(
        db_session,
        build_task_custom_field_value(
            value_id=99,
            task_id=other_task_1_obj.id,
            custom_field_id=other_custom_field_obj.id,
        ),
    )


@pytest.fixture
def seed_db(db_session):
    _persist(db_session, build_role())
    test_user = _persist(
        db_session,
        build_user(),
    )
    test_team = _persist(db_session, build_team())
    _persist(
        db_session,
        build_user_team(user_id=test_user.id, team_id=test_team.id),
    )
    test_project = _persist(
        db_session,
        build_project(team_id=test_team.id),
    )
    _persist(
        db_session,
        build_stream(project_id=test_project.id),
    )
    return db_session
