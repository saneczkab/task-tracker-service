from datetime import datetime, timedelta
from typing import Optional

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.models.user import User
from app.models.team import Team, UserTeam, Role
from app.models.project import Project
from app.models.stream import Stream
from app.models.task import Task, TaskRelation, TaskReminder, TaskHistory
from app.models.push import PushSubscription
from app.models.goal import Goal
from app.models.meta import Status, Priority, ConnectionType
from app.models.tag import Tag, TaskTag
from app.models.custom_field import (
    CustomField,
    CustomFieldType,
    TaskCustomFieldValue,
)
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


class TaskReminderFactory(SQLAlchemyFactory[TaskReminder]):
    __model__ = TaskReminder


class TaskHistoryFactory(SQLAlchemyFactory[TaskHistory]):
    __model__ = TaskHistory


class PushSubscriptionFactory(SQLAlchemyFactory[PushSubscription]):
    __model__ = PushSubscription


class TagFactory(SQLAlchemyFactory[Tag]):
    __model__ = Tag


class CustomFieldFactory(SQLAlchemyFactory[CustomField]):
    __model__ = CustomField


class TaskCustomFieldValueFactory(SQLAlchemyFactory[TaskCustomFieldValue]):
    __model__ = TaskCustomFieldValue


def build_user(
    user_id: int = 42,
    email: str = "test@example.com",
    nickname: str = "test_user",
    password_hash: Optional[str] = None,
) -> User:
    if password_hash is None:
        password_hash = get_password_hash("test_password")
    return UserFactory.build(
        id=user_id,
        email=email,
        nickname=nickname,
        password_hash=password_hash,
        user_teams=[],
        assigned_tasks=[],
    )


def build_team(team_id: int = 42, name: str = "Test team") -> Team:
    return Team(id=team_id, name=name)


def build_project(
    project_id: int = 42, name: str = "Test project", team_id: int = 42
) -> Project:
    return Project(id=project_id, name=name, team_id=team_id)


def build_stream(
    stream_id: int = 42,
    name: str = "Test stream",
    project_id: int = 42,
    position: int = 0,
) -> Stream:
    return Stream(id=stream_id, name=name, project_id=project_id, position=position)


def build_task(
    task_id: int = 42,
    name: str = "Test task",
    stream_id: int = 42,
    description: Optional[str] = None,
    status_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    deadline: Optional[datetime] = None,
    position: int = 1,
) -> Task:
    return Task(
        id=task_id,
        name=name,
        stream_id=stream_id,
        description=description,
        status_id=status_id,
        priority_id=priority_id,
        position=position,
        start_date=start_date,
        deadline=deadline,
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
    return Goal(
        id=goal_id,
        name=name,
        stream_id=stream_id,
        deadline=deadline,
        description=description,
        position=position,
    )


def build_role(role_id: int = 2, name: str = "Editor") -> Role:
    return Role(id=role_id, name=name)


def build_user_team(
    user_team_id: int = 42, user_id: int = 42, team_id: int = 42, role_id: int = 2
) -> UserTeam:
    return UserTeam(
        id=user_team_id,
        user_id=user_id,
        team_id=team_id,
        role_id=role_id,
    )


def build_status(status_id: int = 42, name: str = "To Do") -> Status:
    return Status(id=status_id, name=name)


def build_priority(priority_id: int = 42, name: str = "Low") -> Priority:
    return Priority(id=priority_id, name=name)


def build_connection_type(
    connection_id: int = 42, name: str = "Test connection"
) -> ConnectionType:
    return ConnectionType(id=connection_id, name=name)


def build_task_relation(
    relation_id: int = 42,
    task_id_1: int = 42,
    task_id_2: int = 43,
    connection_id: int = 42,
) -> TaskRelation:
    relation = TaskRelation(
        id=relation_id,
        task_id_1=task_id_1,
        task_id_2=task_id_2,
        connection_id=connection_id,
    )
    relation.connection = build_connection_type(connection_id=connection_id)
    return relation


def build_reminder(
    reminder_id: int = 42,
    task_id: int = 42,
    user_id: int = 42,
    remind_at: Optional[datetime] = None,
    sent: bool = False,
) -> TaskReminder:
    if remind_at is None:
        remind_at = datetime.now() + timedelta(days=7)
    return TaskReminder(
        id=reminder_id,
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at,
        sent=sent,
    )


def build_push_subscription(
    subscription_id: int = 42,
    user_id: int = 42,
    endpoint: str = "https://example.com/",
    p256dh: str = "test-key",
    auth: str = "test-key",
) -> PushSubscription:
    return PushSubscription(
        id=subscription_id,
        user_id=user_id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth,
    )


def build_tag(
    tag_id: int = 42,
    team_id: int = 42,
    name: str = "Tag",
    color: str = "#AABBCC",
) -> Tag:
    return Tag(
        id=tag_id,
        team_id=team_id,
        name=name,
        color=color,
    )


def build_custom_field(
    field_id: int = 42,
    team_id: int = 42,
    name: str = "Custom field",
    field_type: CustomFieldType = CustomFieldType.STRING,
) -> CustomField:
    return CustomField(
        id=field_id,
        team_id=team_id,
        name=name,
        type=field_type,
    )


def build_task_custom_field_value(
    value_id: int = 42,
    task_id: int = 42,
    custom_field_id: int = 42,
    value_string: Optional[str] = None,
    value_text: Optional[str] = None,
    value_bool: Optional[bool] = None,
) -> TaskCustomFieldValue:
    return TaskCustomFieldValue(
        id=value_id,
        task_id=task_id,
        custom_field_id=custom_field_id,
        value_string=value_string,
        value_text=value_text,
        value_date=None,
        value_datetime=None,
        value_bool=value_bool,
    )


def build_task_history(
    history_id: int = 42,
    task_id: int = 42,
    changed_by_id: int = 42,
    field_name: str = "name",
    old_value: str = "",
    new_value: str = "",
    changed_at: Optional[datetime] = None,
) -> TaskHistory:
    if changed_at is None:
        changed_at = datetime.now()
    return TaskHistory(
        id=history_id,
        task_id=task_id,
        changed_by_id=changed_by_id,
        changed_at=changed_at,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
    )
