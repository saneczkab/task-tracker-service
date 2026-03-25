from enum import Enum
from pydantic import BaseModel


class ExportScope(str, Enum):
    all = "all"
    my = "my"


class ExportTarget(str, Enum):
    all = "all"
    team = "team"
    stream = "stream"


class CalendarExport(BaseModel):
    scope: ExportScope
    target: ExportTarget
    target_id: int | None = None

