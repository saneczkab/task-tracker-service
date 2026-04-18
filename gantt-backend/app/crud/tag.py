from sqlalchemy import orm

from app.models import tag


def create_tag(db: orm.Session, team_id: int, name: str, color: str):
    t = tag.Tag(name=name, color=color, team_id=team_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def get_team_tags(db: orm.Session, team_id: int):
    return db.query(tag.Tag).filter(tag.Tag.team_id == team_id).all()


def get_tag_by_id(db: orm.Session, tag_id: int):
    return db.query(tag.Tag).filter(tag.Tag.id == tag_id).first()


def delete_tag(db: orm.Session, t: tag.Tag):
    db.delete(t)
    db.commit()