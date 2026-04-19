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
    STATUS_TODO = 2
    STATUS_DOING = 3
    
    @staticmethod
    def get_task_analytics(
        data_base: orm.Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None
    ) -> analytics_schemas.TaskAnalytics:
        
        query = data_base.query(Task).join(
            Stream, Task.stream_id == Stream.id
        ).join(
            Project, Stream.project_id == Project.id
        ).filter(Project.team_id == team_id)
        
        if period_filter.start_date:
            start = datetime.combine(period_filter.start_date, datetime.min.time())
            query = query.filter(Task.deadline >= start)
        
        if period_filter.end_date:
            end = datetime.combine(period_filter.end_date, datetime.max.time())
            query = query.filter(Task.deadline <= end)
        
        if project_id:
            query = query.filter(Stream.project_id == project_id)
        
        if stream_id:
            query = query.filter(Task.stream_id == stream_id)
        
        total_tasks = query.count()
        completed_tasks = query.filter(Task.status_id == AnalyticsService.STATUS_DONE).count()
        in_progress = query.filter(Task.status_id.in_([AnalyticsService.STATUS_TODO, AnalyticsService.STATUS_DOING])).count()
        overdue = query.filter(
            Task.deadline < datetime.now(),
            Task.status_id != AnalyticsService.STATUS_DONE
        ).count()
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return analytics_schemas.TaskAnalytics(
            total_tasks=total_tasks,
            completed_on_time=completed_tasks,
            in_progress=in_progress,
            overdue=overdue,
            completion_rate=round(completion_rate, 2)
        )
    
    @staticmethod
    def get_users_stats(
        data_base: orm.Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None
    ) -> List[analytics_schemas.UserTaskStats]:
        """Получить статистику по каждому пользователю"""

        users = data_base.query(User).join(UserTeam).filter(UserTeam.team_id == team_id).all()
        
        base_query = data_base.query(Task).join(
            Stream, Task.stream_id == Stream.id
        ).join(
            Project, Stream.project_id == Project.id
        ).filter(Project.team_id == team_id)
        
        if period_filter.start_date:
            start = datetime.combine(period_filter.start_date, datetime.min.time())
            base_query = base_query.filter(Task.deadline >= start)
        
        if period_filter.end_date:
            end = datetime.combine(period_filter.end_date, datetime.max.time())
            base_query = base_query.filter(Task.deadline <= end)
        
        if project_id:
            base_query = base_query.filter(Stream.project_id == project_id)
        
        if stream_id:
            base_query = base_query.filter(Task.stream_id == stream_id)
        
        users_stats = []
        for user in users:
            user_tasks = base_query.join(Task.assigned_users).filter(
                Task.assigned_users.any(user_id=user.id)
            )
            
            total = user_tasks.count()
            completed = user_tasks.filter(Task.status_id == AnalyticsService.STATUS_DONE).count()
            overdue = user_tasks.filter(
                Task.deadline < datetime.now(),
                Task.status_id != AnalyticsService.STATUS_DONE
            ).count()
            in_progress = user_tasks.filter(Task.status_id.in_([AnalyticsService.STATUS_TODO, AnalyticsService.STATUS_DOING])).count()
            
            users_stats.append(analytics_schemas.UserTaskStats(
                user_id=user.id,
                email=user.email,
                nickname=user.nickname,
                total_tasks=total,
                completed_tasks=completed,
                overdue_tasks=overdue,
                in_progress_tasks=in_progress
            ))
        
        return users_stats
    
    @staticmethod
    def get_tasks_list(
        data_base: orm.Session,
        team_id: int,
        period_filter: analytics_schemas.PeriodFilter,
        project_id: Optional[int] = None,
        stream_id: Optional[int] = None
    ) -> List[analytics_schemas.TaskBrief]:
        """Получить список задач для аналитики"""
        
        query = data_base.query(Task).join(
            Stream, Task.stream_id == Stream.id
        ).join(
            Project, Stream.project_id == Project.id
        ).filter(Project.team_id == team_id)
        
        if period_filter.start_date:
            start = datetime.combine(period_filter.start_date, datetime.min.time())
            query = query.filter(Task.deadline >= start)
        
        if period_filter.end_date:
            end = datetime.combine(period_filter.end_date, datetime.max.time())
            query = query.filter(Task.deadline <= end)
        
        if project_id:
            query = query.filter(Stream.project_id == project_id)
        
        if stream_id:
            query = query.filter(Task.stream_id == stream_id)
        
        tasks = []
        for task in query.all():
            assigned_users = [ut.user.email for ut in task.assigned_users] if task.assigned_users else []
            tasks.append(analytics_schemas.TaskBrief(
                id=task.id,
                name=task.name,
                status_id=task.status_id,
                deadline=task.deadline,
                assigned_users=assigned_users
            ))
        
        return tasks
