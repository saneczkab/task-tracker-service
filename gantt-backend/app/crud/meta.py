import fastapi
from sqlalchemy import orm

from app.core import db
from app.models import meta as meta_models

router = fastapi.APIRouter()


def get_team_statuses(data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все статусы в команде team_id"""
    return data_base.query(meta_models.Status).all()


def get_team_priorities(data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все приоритеты в команде team_id"""
    return data_base.query(meta_models.Priority).all()


def get_connection_types(data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все типы связей"""
    return data_base.query(meta_models.ConnectionType).all()
