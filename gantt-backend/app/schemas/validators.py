from datetime import UTC, datetime


def normalize_datetime(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(UTC).replace(tzinfo=None)


def validate_deadline_after_start(
    deadline: datetime | None,
    start_date: datetime | None,
) -> None:
    if not start_date or not deadline:
        return
    if normalize_datetime(deadline) <= normalize_datetime(start_date):
        raise ValueError("deadline должен быть больше start_date")
