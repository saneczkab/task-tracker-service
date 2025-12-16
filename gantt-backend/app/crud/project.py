from sqlalchemy import orm

from app.models import project


def get_project_by_id(data_base: orm.Session, project_id: int):
    """Получить проект по project_id"""
    return data_base.query(project.Project).filter(project.Project.id == project_id).first()


def get_projects_by_team(data_base: orm.Session, team_id: int):
    return data_base.query(project.Project).filter(project.Project.team_id == team_id).all()


def create_project(data_base: orm.Session, team_id: int, project_data):
    new_project = project.Project(
        name=project_data.name,
        team_id=team_id
    )
    data_base.add(new_project)
    data_base.commit()
    data_base.refresh(new_project)
    return new_project


def update_project(data_base: orm.Session, project_obj, update_data):
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(project_obj, field, value)
    data_base.commit()
    data_base.refresh(project_obj)
    return project_obj


def delete_project(data_base: orm.Session, project_obj):
    data_base.delete(project_obj)
    data_base.commit()
