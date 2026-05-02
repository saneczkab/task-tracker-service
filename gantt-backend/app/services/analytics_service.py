from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.crud import analytics as analytics_crud
from app.schemas import analytics as analytics_schemas
from app.models.task import Task


class AnalyticsService:

    @staticmethod
    def get_task_analytics(
        data_base: Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
        filters: Optional[analytics_schemas.AnalyticsFilters] = None,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> analytics_schemas.TaskAnalytics:
        query = analytics_crud.get_base_tasks_query(
            data_base, team_id, period_filter, date_ranges, filters, project_id, stream_id
        )
        total, completed, in_progress, overdue = analytics_crud.get_task_counts(query)

        completion_rate = (completed / total * 100) if total > 0 else 0

        return analytics_schemas.TaskAnalytics(
            total_tasks=total,
            completed_on_time=completed,
            in_progress=in_progress,
            overdue=overdue,
            completion_rate=round(completion_rate, 2),
        )

    @staticmethod
    def get_users_stats(
        data_base: Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
        filters: Optional[analytics_schemas.AnalyticsFilters] = None,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> List[analytics_schemas.UserTaskStats]:
        STATUS_DONE = 4
        STATUS_TODO = 2
        STATUS_DOING = 3

        users_with_tasks = analytics_crud.get_users_with_tasks(
            data_base, team_id, period_filter, date_ranges, filters, project_id, stream_id
        )

        users_stats = []
        for user, user_query in users_with_tasks:
            total = user_query.count()
            if total > 0:
                completed = user_query.filter(Task.status_id == STATUS_DONE).count()
                overdue = user_query.filter(
                    Task.deadline < datetime.now(),
                    Task.status_id != STATUS_DONE,
                ).count()
                in_progress = user_query.filter(
                    Task.status_id.in_([STATUS_TODO, STATUS_DOING])
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
        data_base: Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        date_ranges: Optional[analytics_schemas.AnalyticsDateRanges] = None,
        filters: Optional[analytics_schemas.AnalyticsFilters] = None,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None,
    ) -> List[analytics_schemas.TaskBrief]:
        tasks = analytics_crud.get_tasks_list_query(
            data_base, team_id, period_filter, date_ranges, filters, project_id, stream_id
        )

        result = []
        for task in tasks:
            assigned_users = [ut.user.email for ut in task.assigned_users] if task.assigned_users else []
            result.append(
                analytics_schemas.TaskBrief(
                    id=task.id,
                    name=task.name,
                    status_id=task.status_id,
                    deadline=task.deadline,
                    assigned_users=assigned_users,
                )
            )
        return result
