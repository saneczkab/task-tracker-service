from enum import StrEnum

from pydantic import BaseModel


class ExportScope(StrEnum):
    all = "all"
    my = "my"


class ExportTarget(StrEnum):
    all = "all"
    team = "team"
    stream = "stream"
    teams = "teams"
    projects = "projects"
    streams = "streams"


class CalendarExport(BaseModel):
    scope: ExportScope
    target: ExportTarget
    target_id: int | None = None
    target_ids: list[int] | None = None
