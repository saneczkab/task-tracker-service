import io
import fastapi

from sqlalchemy import orm
from starlette import responses
from app.api import auth
from app.core import db, exception
from app.schemas import calendar as calendar_schemas
from app.services import calendar_service

router = fastapi.APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.post("/export")
def export_calendar(export_options: calendar_schemas.CalendarExport,
                    data_base: orm.Session = fastapi.Depends(db.get_db),
                    current_user=fastapi.Depends(auth.get_current_user), ):
    try:
        calendar_data = calendar_service.export_calendar_service(data_base, current_user.id, export_options)
        return responses.StreamingResponse(io.StringIO(calendar_data), media_type="text/calendar",
                                           headers={"Content-Disposition": "attachment; filename=calendar.ics"}, )
    except exception.NotFoundError as e:
        raise fastapi.HTTPException(404, str(e))
    except exception.ForbiddenError as e:
        raise fastapi.HTTPException(403, str(e))
