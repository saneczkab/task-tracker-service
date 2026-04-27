import fastapi
from sqlalchemy import orm
from datetime import date, timedelta
from typing import Optional

from app.api import auth
from app.core import db
from app.services.analytics_service import AnalyticsService
from app.services.ai_report_service import AIReportService
from app.schemas import analytics as analytics_schemas
from app.models.team import UserTeam

router = fastapi.APIRouter()


@router.get(
    "/api/team/{team_id}/analytics",
    response_model=analytics_schemas.TeamAnalyticsResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
def get_team_analytics(
    team_id: int,
    period: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    project_id: Optional[int] = None,
    stream_id: Optional[int] = None,
    project_ids: Optional[str] = None,
    stream_ids: Optional[str] = None,
    status_ids: Optional[str] = None,
    priority_ids: Optional[str] = None,
    assigned_user_ids: Optional[str] = None,
    is_ai_needed: bool = False,
    data_base: orm.Session = fastapi.Depends(db.get_db),
    current_user: dict = fastapi.Depends(auth.get_current_user),
):
    from app.models.team import Team
    from app.models.user import User
    from app.models.team import UserTeam

    team = data_base.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise fastapi.HTTPException(status_code=404, detail="Team not found")

    period_filter = analytics_schemas.PeriodFilter(
        start_date=start_date, end_date=end_date, period=period
    )

    if period == "week":
        period_filter.start_date = date.today() - timedelta(days=7)
    elif period == "month":
        period_filter.start_date = date.today() - timedelta(days=30)

    parsed_filters = {
        "project_ids": [int(x) for x in project_ids.split(',') if x.strip()] if project_ids else None,
        "stream_ids": [int(x) for x in stream_ids.split(',') if x.strip()] if stream_ids else None,
        "status_ids": [int(x) for x in status_ids.split(',') if x.strip()] if status_ids else None,
        "priority_ids": [int(x) for x in priority_ids.split(',') if x.strip()] if priority_ids else None,
        "assigned_user_ids": [int(x) for x in assigned_user_ids.split(',') if x.strip()] if assigned_user_ids else None,
    }

    filters = None
    if any(parsed_filters.values()):
        filters = analytics_schemas.AnalyticsFilters(**parsed_filters)

    analytics = AnalyticsService.get_task_analytics(
        data_base, team_id, period_filter, filters, project_id, stream_id
    )

    users_stats = AnalyticsService.get_users_stats(
        data_base, team_id, period_filter, filters, project_id, stream_id
    )

    tasks = AnalyticsService.get_tasks_list(
        data_base, team_id, period_filter, filters, project_id, stream_id
    )

    users = (
        data_base.query(User)
        .join(UserTeam, UserTeam.user_id == User.id)
        .filter(UserTeam.team_id == team_id)
        .all()
    )

    ai_summary = ""
    if is_ai_needed:
        ai_summary = AIReportService.generate_summary(
            analytics, users_stats, tasks, team.name, period
        )

    return analytics_schemas.TeamAnalyticsResponse(
        team_id=team_id,
        team_name=team.name,
        analytics=analytics,
        users_stats=users_stats,
        tasks=tasks,
        users=[{"id": u.id, "email": u.email, "nickname": u.nickname} for u in users],
        period=period_filter,
        filters=filters,
        ai_summary=ai_summary,
    )
