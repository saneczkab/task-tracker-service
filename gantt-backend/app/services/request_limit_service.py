from sqlalchemy.orm import Session
from app.models.request_limit import RequestLimit
from datetime import date, timedelta
from fastapi import HTTPException


class RequestLimitService:
    """Ограничитель запросов к ИИ"""
    DAILY_LIMIT = 1

    @staticmethod
    def get_usage(db: Session, user_id: int) -> dict:
        today = date.today()
        entry = db.query(RequestLimit).filter(
            RequestLimit.user_id == user_id,
            RequestLimit.target_date == today
        ).first()
        used = entry.request_count if entry else 0
        return {
            "limit": RequestLimitService.DAILY_LIMIT,
            "used": used,
            "remaining": max(0, RequestLimitService.DAILY_LIMIT - used),
            "reset_time": (today + timedelta(days=1)).isoformat()
        }

    @staticmethod
    def check_and_increment(db: Session, user_id: int) -> dict:
        today = date.today()
        entry = db.query(RequestLimit).filter(
            RequestLimit.user_id == user_id,
            RequestLimit.target_date == today
        ).first()
        if not entry:
            entry = RequestLimit(user_id=user_id, target_date=today, request_count=0)
            db.add(entry)
            db.commit()

        if entry.request_count >= RequestLimitService.DAILY_LIMIT:
            usage = {
                "limit": RequestLimitService.DAILY_LIMIT,
                "used": entry.request_count,
                "remaining": 0,
                "reset_time": (today + timedelta(days=1)).isoformat()
            }
            raise HTTPException(
                status_code=429,
                detail={
                    "message": f"Превышен лимит запросов. Лимит {RequestLimitService.DAILY_LIMIT} запросов в день.",
                    "request_limit": usage
                }
            )

        entry.request_count += 1
        db.commit()

        return {
            "limit": RequestLimitService.DAILY_LIMIT,
            "used": entry.request_count,
            "remaining": max(0, RequestLimitService.DAILY_LIMIT - entry.request_count),
            "reset_time": (today + timedelta(days=1)).isoformat()
        }
