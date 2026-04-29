from sqlalchemy import orm, func
from datetime import datetime
from typing import Optional, List
from app.models.task import Task
from app.models.project import Project
from app.models.stream import Stream
from app.models.user import User
from app.models.team import UserTeam
from app.schemas import analytics as analytics_schemas


class AnalyticsService:
    STATUS_DONE = 4
    STATUS_NO_STATUS = 1
    STATUS_TODO = 2
    STATUS_DOING = 3

    @staticmethod
    def _apply_filters(
        query,
        filters: analytics_schemas.AnalyticsFilters,
        include_stream_join: bool = True,
    ):
        """Применить фильтры к запросу"""
        from app.models.meta import UserTask
        from app.models import tag as tag_models

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
                query = query.join(Stream, Task.stream_id == Stream.id).join(
                    Project, Stream.project_id == Project.id
                )
            has_project = True

        if filters.project_ids:
            query = query.filter(Project.id.in_(filters.project_ids))

        if filters.stream_ids:
            query = query.filter(Task.stream_id.in_(filters.stream_ids))

        if filters.status_ids:
            query = query.filter(Task.status_id.in_(filters.status_ids))

        if filters.priority_ids:
            query = query.filter(Task.priority_id.in_(filters.priority_ids))

        if filters.assigned_user_ids:
            if "UserTask" not in str(query):
                query = query.join(UserTask, Task.id == UserTask.task_id)
            query = query.filter(UserTask.user_id.in_(filters.assigned_user_ids))
            query = query.distinct()

        if filters.assignee_emails:
            if "UserTask" not in str(query):
                query = query.join(UserTask, Task.id == UserTask.task_id)
            if "User" not in str(query):
                query = query.join(User, UserTask.user_id == User.id)
            query = query.filter(User.email.in_(filters.assignee_emails))
            query = query.distinct()

        if filters.tag_ids:
            if "TaskTag" not in str(query):
                query = query.join(
                    tag_models.TaskTag, Task.id == tag_models.TaskTag.task_id
                )
            query = query.filter(tag_models.TaskTag.tag_id.in_(filters.tag_ids))
            query = query.distinct()

        return query

    @staticmethod
    def _apply_date_ranges(
        query, date_ranges: Optional[analytics_schemas.AnalyticsDateRanges]
    ):
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

    @staticmethod
    def get_task_analytics(
        data_base: orm.Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
        filters: Optional[analytics_schemas.AnalyticsFilters] = None,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> analytics_schemas.TaskAnalytics:

        team_ids = None
        if filters and filters.team_ids:
            team_ids = filters.team_ids

        query = (
            data_base.query(Task)
            .join(Stream, Task.stream_id == Stream.id)
            .join(Project, Stream.project_id == Project.id)
        )

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

        query = AnalyticsService._apply_date_ranges(query, date_ranges)

        if project_id:
            query = query.filter(Stream.project_id == project_id)

        if stream_id:
            query = query.filter(Task.stream_id == stream_id)

        if filters:
            query = AnalyticsService._apply_filters(
                query, filters, include_stream_join=False
            )

        total_tasks = query.count()
        completed_tasks = query.filter(
            Task.status_id == AnalyticsService.STATUS_DONE
        ).count()
        in_progress = query.filter(
            Task.status_id.in_(
                [
                    AnalyticsService.STATUS_NO_STATUS,
                    AnalyticsService.STATUS_TODO,
                    AnalyticsService.STATUS_DOING,
                ]
            )
        ).count()
        overdue = query.filter(
            Task.deadline < datetime.now(),
            Task.status_id != AnalyticsService.STATUS_DONE,
        ).count()

        completion_rate = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        return analytics_schemas.TaskAnalytics(
            total_tasks=total_tasks,
            completed_on_time=completed_tasks,
            in_progress=in_progress,
            overdue=overdue,
            completion_rate=round(completion_rate, 2),
        )

    @staticmethod
    def get_users_stats(
        data_base: orm.Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
        filters: Optional[analytics_schemas.AnalyticsFilters] = None,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> List[analytics_schemas.UserTaskStats]:
        """Получить статистику по каждому пользователю"""
        from app.models.meta import UserTask

        team_ids = None
        if filters and filters.team_ids:
            team_ids = filters.team_ids

        users_query = data_base.query(User).join(UserTeam)
        if team_ids:
            users_query = users_query.filter(UserTeam.team_id.in_(team_ids))
        else:
            users_query = users_query.filter(UserTeam.team_id == team_id)
        users = users_query.distinct().all()

        users_stats = []
        for user in users:
            user_query = (
                data_base.query(Task)
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

            user_query = AnalyticsService._apply_date_ranges(user_query, date_ranges)

            if project_id:
                user_query = user_query.filter(Stream.project_id == project_id)

            if stream_id:
                user_query = user_query.filter(Task.stream_id == stream_id)

            if filters:
                if (
                    filters.assigned_user_ids
                    and user.id not in filters.assigned_user_ids
                ):
                    continue
                if (
                    filters.assignee_emails
                    and user.email not in filters.assignee_emails
                ):
                    continue

                user_query = AnalyticsService._apply_filters(
                    user_query, filters, include_stream_join=False
                )

            total = user_query.count()
            if total > 0:
                completed = user_query.filter(
                    Task.status_id == AnalyticsService.STATUS_DONE
                ).count()
                overdue = user_query.filter(
                    Task.deadline < datetime.now(),
                    Task.status_id != AnalyticsService.STATUS_DONE,
                ).count()
                in_progress = user_query.filter(
                    Task.status_id.in_(
                        [AnalyticsService.STATUS_TODO, AnalyticsService.STATUS_DOING]
                    )
                ).count()
            else:
                completed = overdue = in_progress = 0

            users_stats.append(
                analytics_schemas.UserTaskStats(
                    user_id=user.id,
                    email=user.email,
                    nickname=user.nickname,
                    total_tasks=total,
                    completed_tasks=completed,
                    overdue_tasks=overdue,
                    in_progress_tasks=in_progress,
                )
            )

        return users_stats

    @staticmethod
    def get_tasks_list(
        data_base: orm.Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
        filters: Optional[analytics_schemas.AnalyticsFilters] = None,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> List[analytics_schemas.TaskBrief]:
        """Получить список задач для аналитики"""
        team_ids = None
        if filters and filters.team_ids:
            team_ids = filters.team_ids

        query = (
            data_base.query(Task)
            .join(Stream, Task.stream_id == Stream.id)
            .join(Project, Stream.project_id == Project.id)
        )

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

        query = AnalyticsService._apply_date_ranges(query, date_ranges)

        if project_id:
            query = query.filter(Stream.project_id == project_id)

        if stream_id:
            query = query.filter(Task.stream_id == stream_id)

        if filters:
            query = AnalyticsService._apply_filters(
                query, filters, include_stream_join=False
            )

        tasks = []
        for task in query.all():
            assigned_users = (
                [ut.user.email for ut in task.assigned_users]
                if task.assigned_users
                else []
            )
            tasks.append(
                analytics_schemas.TaskBrief(
                    id=task.id,
                    name=task.name,
                    status_id=task.status_id,
                    deadline=task.deadline,
                    assigned_users=assigned_users,
                )
            )

        return tasks
