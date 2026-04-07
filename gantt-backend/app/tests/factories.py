from datetime import datetime, timedelta
from typing import Optional

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.models.user import User
from app.models.team import Team, UserTeam, Role
from app.models.project import Project
from app.models.stream import Stream
from app.models.task import Task, TaskRelation
from app.models.goal import Goal
from app.models.meta import Status, Priority, ConnectionType
from app.core.security import get_password_hash


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User


class TeamFactory(SQLAlchemyFactory[Team]):
    __model__ = Team


class UserTeamFactory(SQLAlchemyFactory[UserTeam]):
    __model__ = UserTeam


class ProjectFactory(SQLAlchemyFactory[Project]):
    __model__ = Project


class StreamFactory(SQLAlchemyFactory[Stream]):
    __model__ = Stream


class TaskFactory(SQLAlchemyFactory[Task]):
    __model__ = Task


class GoalFactory(SQLAlchemyFactory[Goal]):
    __model__ = Goal


class StatusFactory(SQLAlchemyFactory[Status]):
    __model__ = Status


class PriorityFactory(SQLAlchemyFactory[Priority]):
    __model__ = Priority


class ConnectionTypeFactory(SQLAlchemyFactory[ConnectionType]):
    __model__ = ConnectionType


class TaskRelationFactory(SQLAlchemyFactory[TaskRelation]):
    __model__ = TaskRelation


def build_user(
    user_id: int = 42, email: str = "test@example.com", nickname: str = "test_user"
) -> User:
    return UserFactory.build(
        id=user_id,
        email=email,
        nickname=nickname,
        password_hash=get_password_hash("test_password"),
        user_teams=[],
        assigned_tasks=[],
    )


def build_team(team_id: int = 42, name: str = "Test team") -> Team:
    return TeamFactory.build(id=team_id, name=name, user_teams=[], projects=[])


def build_project(
    project_id: int = 42, name: str = "Test project", team_id: int = 42
) -> Project:
    return ProjectFactory.build(id=project_id, name=name, team_id=team_id, streams=[])


def build_stream(
    stream_id: int = 42, name: str = "Test stream", project_id: int = 42
) -> Stream:
    return StreamFactory.build(id=stream_id, name=name, project_id=project_id, goals=[])


def build_task(
    task_id: int = 42,
    name: str = "Test task",
    stream_id: int = 42,
    description: Optional[str] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    position: int = 1,
) -> Task:
    return TaskFactory.build(
        id=task_id,
        name=name,
        stream_id=stream_id,
        description=description,
        status_id=status_id,
        priority_id=priority_id,
        position=position,
        start_date=None,
        deadline=None,
        assigned_users=[],
    )


def build_goal(
    goal_id: int = 42,
    name: str = "Test goal",
    stream_id: int = 42,
    deadline: Optional[datetime] = None,
    description: Optional[str] = None,
    position: int = 1,
) -> Goal:
    if deadline is None:
        deadline = datetime.now() + timedelta(days=30)
    return GoalFactory.build(
        id=goal_id,
        name=name,
        stream_id=stream_id,
        deadline=deadline,
        description=description,
        position=position,
    )


def build_role(role_id: int = 2) -> Role:
    return Role(role_id)


def build_user_team(
    user_team_id: int = 42, user_id: int = 42, team_id: int = 42, role_id: int = 2
) -> UserTeam:
    return UserTeamFactory.build(
        id=user_team_id,
        user_id=user_id,
        team_id=team_id,
        role_id=role_id,
        user=None,
        team=None,
        role=None,
    )


def build_status(status_id: int = 42, name: str = "To Do") -> Status:
    return StatusFactory.build(id=status_id, name=name)


def build_priority(priority_id: int = 42, name: str = "Low") -> Priority:
    return PriorityFactory.build(id=priority_id, name=name)


def build_connection_type(
    connection_id: int = 42, name: str = "Test connection"
) -> ConnectionType:
    return ConnectionTypeFactory.build(id=connection_id, name=name)


def build_task_relation(
    relation_id: int = 42,
    task_id_1: int = 42,
    task_id_2: int = 43,
    connection_id: int = 42,
) -> TaskRelation:
    relation = TaskRelationFactory.build(
        id=relation_id,
        task_id_1=task_id_1,
        task_id_2=task_id_2,
        connection_id=connection_id,
    )
    relation.connection = build_connection_type(connection_id=connection_id)
    return relation
