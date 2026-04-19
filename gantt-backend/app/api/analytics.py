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


@router.get("/team/{team_id}/analytics", response_model=analytics_schemas.TeamAnalyticsResponse,
            status_code=fastapi.status.HTTP_200_OK)
def get_team_analytics(
    team_id: int,
    period: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    project_id: Optional[int] = None,
    stream_id: Optional[int] = None,
    data_base: orm.Session = fastapi.Depends(db.get_db),
    current_user: dict = fastapi.Depends(auth.get_current_user)
):
    from app.models.team import Team
    from app.models.user import User
    from app.models.team import UserTeam
    
    team = data_base.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise fastapi.HTTPException(status_code=404, detail="Team not found")
    
    period_filter = analytics_schemas.PeriodFilter(
        start_date=start_date,
        end_date=end_date,
        period=period
    )
    
    if period == 'week':
        period_filter.start_date = date.today() - timedelta(days=7)
    elif period == 'month':
        period_filter.start_date = date.today() - timedelta(days=30)
    
    analytics = AnalyticsService.get_task_analytics(
        data_base, team_id, period_filter, project_id, stream_id
    )

    users_stats = AnalyticsService.get_users_stats(
        data_base, team_id, period_filter, project_id, stream_id
    )

    tasks = AnalyticsService.get_tasks_list(
        data_base, team_id, period_filter, project_id, stream_id
    )

    users = data_base.query(User).join(UserTeam, UserTeam.user_id == User.id).filter(
        UserTeam.team_id == team_id
    ).all()

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
        ai_summary=ai_summary
    )
