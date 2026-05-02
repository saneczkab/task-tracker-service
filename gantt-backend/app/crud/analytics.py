from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.models.task import Task
from app.models.project import Project
from app.models.stream import Stream
from app.models.user import User
from app.models.team import UserTeam
from app.models.meta import UserTask
from app.models import tag as tag_models
from app.schemas import analytics as analytics_schemas


def _apply_filters(query, filters: analytics_schemas.AnalyticsFilters, include_stream_join: bool = True):
    """Применить фильтры к запросу"""
    has_stream = "Stream" in str(query) or "stream" in str(query)
    has_project = "Project" in str(query) or "project" in str(query)

    if include_stream_join and not has_stream:
        if filters.stream_ids or filters.project_ids:
            query = query.join(Stream, Task.stream_id == Stream.id)
            has_stream = True

    if not has_project and filters.project_ids:
        if has_stream:
            query = query.join(Project, Stream.project_id == Project.id)
        else:
            query = query.join(Stream, Task.stream_id == Stream.id).join(Project, Stream.project_id == Project.id)

    if filters.project_ids:
        query = query.filter(Project.id.in_(filters.project_ids))

    if filters.stream_ids:
        query = query.filter(Task.stream_id.in_(filters.stream_ids))

    if filters.status_ids:
        query = query.filter(Task.status_id.in_(filters.status_ids))

    if filters.priority_ids:
        query = query.filter(Task.priority_id.in_(filters.priority_ids))

    if filters.assigned_user_ids:
        query = query.join(UserTask, Task.id == UserTask.task_id).filter(
            UserTask.user_id.in_(filters.assigned_user_ids)
        ).distinct()

    if filters.assignee_emails:
        query = query.join(UserTask, Task.id == UserTask.task_id).join(
            User, UserTask.user_id == User.id
        ).filter(User.email.in_(filters.assignee_emails)).distinct()

    if filters.tag_ids:
        query = query.join(tag_models.TaskTag, Task.id == tag_models.TaskTag.task_id).filter(
            tag_models.TaskTag.tag_id.in_(filters.tag_ids)
        ).distinct()

    return query


def _apply_date_ranges(query, date_ranges: Optional[analytics_schemas.AnalyticsDateRanges]):
    """Применить фильтры по датам"""
    if not date_ranges:
        return query

    if date_ranges.start_date_from:
        start = datetime.combine(date_ranges.start_date_from, datetime.min.time())
        query = query.filter(Task.start_date >= start)

    if date_ranges.start_date_to:
        end = datetime.combine(date_ranges.start_date_to, datetime.max.time())
        query = query.filter(Task.start_date <= end)

    if date_ranges.deadline_from:
        start = datetime.combine(date_ranges.deadline_from, datetime.min.time())
        query = query.filter(Task.deadline >= start)

    if date_ranges.deadline_to:
        end = datetime.combine(date_ranges.deadline_to, datetime.max.time())
        query = query.filter(Task.deadline <= end)

    return query


def get_base_tasks_query(
    db: Session,
    team_id: int,
    period_filter: analytics_schemas.PeriodFilter,
    date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
    filters: Optional[analytics_schemas.AnalyticsFilters] = None,
    project_id: Optional[int] = None,
    stream_id: Optional[int] = None,
):
    """Базовый запрос задач с фильтрами"""
    team_ids = filters.team_ids if filters and filters.team_ids else None

    query = db.query(Task).join(Stream, Task.stream_id == Stream.id).join(Project, Stream.project_id == Project.id)

    if team_ids:
        query = query.filter(Project.team_id.in_(team_ids))
    else:
        query = query.filter(Project.team_id == team_id)

    if period_filter.start_date:
        start = datetime.combine(period_filter.start_date, datetime.min.time())
        query = query.filter(Task.deadline >= start)

    if period_filter.end_date:
        end = datetime.combine(period_filter.end_date, datetime.max.time())
        query = query.filter(Task.deadline <= end)

    query = _apply_date_ranges(query, date_ranges)

    if project_id:
        query = query.filter(Stream.project_id == project_id)

    if stream_id:
        query = query.filter(Task.stream_id == stream_id)

    if filters:
        query = _apply_filters(query, filters, include_stream_join=False)

    return query


def get_task_counts(query) -> tuple[int, int, int, int]:
    """Подсчёт задач: total, completed, in_progress, overdue"""
    STATUS_DONE = 4
    STATUS_NO_STATUS = 1
    STATUS_TODO = 2
    STATUS_DOING = 3

    total_tasks = query.count()
    completed_tasks = query.filter(Task.status_id == STATUS_DONE).count()
    in_progress = query.filter(
        Task.status_id.in_([STATUS_NO_STATUS, STATUS_TODO, STATUS_DOING])
    ).count()
    overdue = query.filter(
        Task.deadline < datetime.now(),
        Task.status_id != STATUS_DONE,
    ).count()
    return total_tasks, completed_tasks, in_progress, overdue


def get_users_with_tasks(
    db: Session,
    team_id: int,
    period_filter: analytics_schemas.PeriodFilter,
    date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
    filters: Optional[analytics_schemas.AnalyticsFilters] = None,
    project_id: Optional[int] = None,
    stream_id: Optional[int] = None,
):
    """Получить пользователей команды с их запросами задач"""
    team_ids = filters.team_ids if filters and filters.team_ids else None

    users_query = db.query(User).join(UserTeam)
    if team_ids:
        users_query = users_query.filter(UserTeam.team_id.in_(team_ids))
    else:
        users_query = users_query.filter(UserTeam.team_id == team_id)
    users = users_query.distinct().all()

    result = []
    for user in users:
        user_query = (
            db.query(Task)
            .join(Stream, Task.stream_id == Stream.id)
            .join(Project, Stream.project_id == Project.id)
            .join(UserTask, Task.id == UserTask.task_id)
            .filter(UserTask.user_id == user.id)
        )

        if team_ids:
            user_query = user_query.filter(Project.team_id.in_(team_ids))
        else:
            user_query = user_query.filter(Project.team_id == team_id)

        if period_filter.start_date:
            start = datetime.combine(period_filter.start_date, datetime.min.time())
            user_query = user_query.filter(Task.deadline >= start)

        if period_filter.end_date:
            end = datetime.combine(period_filter.end_date, datetime.max.time())
            user_query = user_query.filter(Task.deadline <= end)

        user_query = _apply_date_ranges(user_query, date_ranges)

        if project_id:
            user_query = user_query.filter(Stream.project_id == project_id)

        if stream_id:
            user_query = user_query.filter(Task.stream_id == stream_id)

        if filters:
            if filters.assigned_user_ids and user.id not in filters.assigned_user_ids:
                continue
            if filters.assignee_emails and user.email not in filters.assignee_emails:
                continue
            user_query = _apply_filters(user_query, filters, include_stream_join=False)

        result.append((user, user_query))
    return result


def get_tasks_list_query(
    db: Session,
    team_id: int,
    period_filter: analytics_schemas.PeriodFilter,
    date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
    filters: Optional[analytics_schemas.AnalyticsFilters] = None,
    project_id: Optional[int] = None,
    stream_id: Optional[int] = None,
):
    """Получить список задач"""
    query = get_base_tasks_query(db, team_id, period_filter, date_ranges, filters, project_id, stream_id)
    return query.all()
