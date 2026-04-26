from sqlalchemy import Column, ForeignKey, Integer, String, orm, UniqueConstraint

from app.models import base


class Tag(base.Base):
    __tablename__ = "Tags"
    __table_args__ = (UniqueConstraint("name", "team_id", name="uq_tag_name_team"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("Teams.id"), nullable=False)

    team = orm.relationship("Team", back_populates="tags")
    task_links = orm.relationship("TaskTag", back_populates="tag", cascade="all, delete-orphan")


class TaskTag(base.Base):
    __tablename__ = "TaskTags"

    task_id = Column(Integer, ForeignKey("Tasks.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("Tags.id"), primary_key=True)

    task = orm.relationship("Task", back_populates="tags")
    tag = orm.relationship("Tag", back_populates="task_links")
