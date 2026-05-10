from datetime import date, datetime

from pydantic import BaseModel


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
    deadline: datetime | None
    assigned_users: list[str]


class PeriodFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    period: str | None = None


class AnalyticsFilters(BaseModel):
    team_ids: list[int] | None = None
    project_ids: list[int] | None = None
    stream_ids: list[int] | None = None
    status_ids: list[int] | None = None
    priority_ids: list[int] | None = None
    assigned_user_ids: list[int] | None = None
    tag_ids: list[int] | None = None
    assignee_emails: list[str] | None = None


class AnalyticsDateRanges(BaseModel):
    start_date_from: date | None = None
    start_date_to: date | None = None
    deadline_from: date | None = None
    deadline_to: date | None = None


class RequestLimitInfo(BaseModel):
    limit: int
    used: int
    remaining: int
    reset_time: str


class TeamAnalyticsResponse(BaseModel):
    team_id: int
    team_name: str
    analytics: TaskAnalytics
    users_stats: list[UserTaskStats]
    tasks: list[TaskBrief]
    users: list[dict]
    period: PeriodFilter
    filters: AnalyticsFilters | None = None
    date_ranges: AnalyticsDateRanges | None = None
    ai_summary: str | None = None
    request_limit: RequestLimitInfo
