from datetime import date, timedelta

import fastapi
from sqlalchemy import orm

from app.api import auth
from app.core import db
from app.models.team import UserTeam
from app.schemas import analytics as analytics_schemas
from app.services.ai_report_service import AIReportService
from app.services.analytics_service import AnalyticsService
from app.services.request_limit_service import RequestLimitService

router = fastapi.APIRouter()


@router.get(
    "/api/team/{team_id}/analytics",
    response_model=analytics_schemas.TeamAnalyticsResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
def get_team_analytics(
    team_id: int,
    period: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    start_date_from: date | None = None,
    start_date_to: date | None = None,
    deadline_from: date | None = None,
    deadline_to: date | None = None,
    project_id: int | None = None,
    stream_id: int | None = None,
    team_ids: str | None = None,
    project_ids: str | None = None,
    stream_ids: str | None = None,
    status_ids: str | None = None,
    priority_ids: str | None = None,
    assigned_user_ids: str | None = None,
    tag_ids: str | None = None,
    assignee_emails: str | None = None,
    is_ai_needed: bool = False,
    data_base: orm.Session = fastapi.Depends(db.get_db),
    current_user: dict = fastapi.Depends(auth.get_current_user),
):
    from app.models.team import Team
    from app.models.user import User

    period_filter = analytics_schemas.PeriodFilter(
        start_date=start_date, end_date=end_date, period=period
    )

    if period == "week":
        period_filter.start_date = date.today() - timedelta(days=7)
    elif period == "month":
        period_filter.start_date = date.today() - timedelta(days=30)

    def _parse_int_csv(value: str | None) -> list[int] | None:
        if not value:
            return None
        parsed = [int(x) for x in value.split(",") if x.strip()]
        return parsed or None

    def _parse_str_csv(value: str | None) -> list[str] | None:
        if not value:
            return None
        parsed = [x.strip() for x in value.split(",") if x.strip()]
        return parsed or None

    parsed_filters = {
        "team_ids": _parse_int_csv(team_ids),
        "project_ids": _parse_int_csv(project_ids),
        "stream_ids": _parse_int_csv(stream_ids),
        "status_ids": _parse_int_csv(status_ids),
        "priority_ids": _parse_int_csv(priority_ids),
        "assigned_user_ids": _parse_int_csv(assigned_user_ids),
        "tag_ids": _parse_int_csv(tag_ids),
        "assignee_emails": _parse_str_csv(assignee_emails),
    }

    filters = None
    if any(parsed_filters.values()):
        filters = analytics_schemas.AnalyticsFilters(**parsed_filters)

    resolved_team_id = team_id
    if filters and filters.team_ids and len(filters.team_ids) == 1:
        resolved_team_id = filters.team_ids[0]

    team = data_base.query(Team).filter(Team.id == resolved_team_id).first()
    if not team:
        raise fastapi.HTTPException(status_code=404, detail="Team not found")

    effective_deadline_from = deadline_from or start_date
    effective_deadline_to = deadline_to or end_date

    date_ranges = analytics_schemas.AnalyticsDateRanges(
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        deadline_from=effective_deadline_from,
        deadline_to=effective_deadline_to,
    )

    analytics = AnalyticsService.get_task_analytics(
        data_base, team_id, period_filter, date_ranges, filters, project_id, stream_id
    )
    users_stats = AnalyticsService.get_users_stats(
        data_base, team_id, period_filter, date_ranges, filters, project_id, stream_id
    )
    tasks = AnalyticsService.get_tasks_list(
        data_base, team_id, period_filter, date_ranges, filters, project_id, stream_id
    )

    users = (
        data_base.query(User)
        .join(UserTeam, UserTeam.user_id == User.id)
        .filter(
            UserTeam.team_id.in_(
                filters.team_ids if filters and filters.team_ids else [team_id]
            )
        )
        .all()
    )

    user_id = current_user.id

    ai_summary = None
    request_limit_info = None

    if is_ai_needed:
        try:
            request_limit_info = RequestLimitService.check_and_increment(
                data_base, user_id
            )
            ai_summary = AIReportService.generate_summary(
                analytics, users_stats, tasks, team.name, period
            )

        except fastapi.HTTPException as e:
            if e.status_code == 429:
                request_limit_info = RequestLimitService.get_usage(data_base, user_id)
                e.detail = {
                    "message": f"Превышен лимит запросов. Лимит {request_limit_info['limit']} запросов в день.",
                    "request_limit": request_limit_info,
                }
            raise e
        except Exception as e:
            print(f"AI generation failed: {e}")
            ai_summary = AIReportService._fallback_summary(analytics, team.name, period)
            if request_limit_info is None:
                request_limit_info = RequestLimitService.get_usage(data_base, user_id)
    else:
        request_limit_info = RequestLimitService.get_usage(data_base, user_id)

    if request_limit_info is None:
        request_limit_info = {
            "limit": RequestLimitService.DAILY_LIMIT,
            "used": -1,
            "remaining": -1,
            "reset_time": (date.today() + timedelta(days=1)).isoformat(),
        }

    return analytics_schemas.TeamAnalyticsResponse(
        team_id=team.id,
        team_name=team.name,
        analytics=analytics,
        users_stats=users_stats,
        tasks=tasks,
        users=[{"id": u.id, "email": u.email, "nickname": u.nickname} for u in users],
        period=period_filter,
        filters=filters,
        date_ranges=date_ranges,
        ai_summary=ai_summary or "",
        request_limit=request_limit_info,
    )
