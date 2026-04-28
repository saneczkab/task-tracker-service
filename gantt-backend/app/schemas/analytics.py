from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class TaskAnalytics(BaseModel):
    total_tasks: int
    completed_on_time: int
    in_progress: int
    overdue: int
    completion_rate: float


class UserTaskStats(BaseModel):
    user_id: int
    email: str
    nickname: str
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    in_progress_tasks: int


class TaskBrief(BaseModel):
    id: int
    name: str
    status_id: int
    deadline: Optional[datetime]
    assigned_users: List[str]


class PeriodFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    period: Optional[str] = None


class AnalyticsFilters(BaseModel):
    project_ids: Optional[List[int]] = None
    stream_ids: Optional[List[int]] = None
    status_ids: Optional[List[int]] = None
    priority_ids: Optional[List[int]] = None
    assigned_user_ids: Optional[List[int]] = None


class RequestLimitInfo(BaseModel):
    limit: int
    used: int
    remaining: int
    reset_time: str


class TeamAnalyticsResponse(BaseModel):
    team_id: int
    team_name: str
    analytics: TaskAnalytics
    users_stats: List[UserTaskStats]
    tasks: List[TaskBrief]
    users: List[dict]
    period: PeriodFilter
    filters: Optional[AnalyticsFilters] = None
    ai_summary: Optional[str] = None
    request_limit: RequestLimitInfo
