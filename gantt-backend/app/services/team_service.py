from sqlalchemy import orm

from app.core import exception
from app.crud import team as team_crud
from app.models import goal, project, role, stream, task, team


def check_team_permissions(data_base: orm.Session, team_id: int, user_id: int, need_lead=False):
    team_obj = team_crud.get_team_by_id(data_base, team_id)
    if not team_obj:
        raise exception.NotFoundError("Команда не найдена")

    member = team_crud.get_user_team(data_base, team_id, user_id)
    if not member:
        raise exception.ForbiddenError("Вы не состоите в этой команде")

    if need_lead and member.role_id != role.Role.EDITOR:
        raise exception.ForbiddenError("Недостаточно прав")

    return member


def get_team_users_service(data_base: orm.Session, team_id: int, user_id: int):
    check_team_permissions(data_base, team_id, user_id)

    users = team_crud.get_team_users(data_base, team_id)

    response = []
    for member in users:
        response.append({
            "id": member.user.id,
            "email": member.user.email,
            "nickname": member.user.nickname,
            "role": "Editor" if member.role_id == role.Role.EDITOR else "Reader"
        })

    return response


def create_team_service(data_base: orm.Session, owner_id: int, create_data):
    team_obj = team_crud.create_team(data_base, create_data.name)

    team_crud.add_user_to_team(data_base, team_obj.id, owner_id, role.Role.EDITOR)

    data_base.commit()
    data_base.refresh(team_obj)
    return team_obj


def update_team_service(data_base: orm.Session, team_id: int, user_id: int, update_data):
    team_obj = team_crud.get_team_by_id(data_base, team_id)
    if not team_obj:
        raise exception.NotFoundError("Команда не найдена")

    check_team_permissions(data_base, team_id, user_id, need_lead=True)

    if update_data.name:
        team_obj.name = update_data.name

    if update_data.newUsers:
        for email in update_data.newUsers:
            user = team_crud.get_user_by_email(data_base, email)
            if not user:
                raise exception.NotFoundError(f"Пользователь {email} не найден")

            if not team_crud.get_user_team(data_base, team_id, user.id):
                team_crud.add_user_to_team(data_base, team_id, user.id, role.Role.READER)

    if update_data.deleteUsers:
        for email in update_data.deleteUsers:
            user = team_crud.get_user_by_email(data_base, email)
            if not user:
                raise exception.NotFoundError(f"Пользователь {email} не найден")

            team_crud.delete_user_from_team(data_base, team_id, user.id)

    data_base.commit()
    data_base.refresh(team_obj)
    return team_obj


def delete_team_service(db: orm.Session, team_id: int, user_id: int):
    team_obj = team_crud.get_team_by_id(db, team_id)
    if not team_obj:
        raise exception.NotFoundError("Команда не найдена")

    check_team_permissions(db, team_id, user_id, need_lead=True)

    projects = db.query(project.Project).filter_by(team_id=team_id).all()
    project_ids = [p.id for p in projects]

    if project_ids:
        streams = db.query(stream.Stream).filter(stream.Stream.project_id.in_(project_ids)).all()
        stream_ids = [s.id for s in streams]

        if stream_ids:
            db.query(task.Task).filter(task.Task.stream_id.in_(stream_ids)).delete(synchronize_session=False)
            db.query(goal.Goal).filter(goal.Goal.stream_id.in_(stream_ids)).delete(synchronize_session=False)

        db.query(stream.Stream).filter(stream.Stream.project_id.in_(project_ids)).delete(synchronize_session=False)
        db.query(project.Project).filter(project.Project.id.in_(project_ids)).delete(synchronize_session=False)

    db.query(team.UserTeam).filter(team.UserTeam.team_id == team_id).delete(synchronize_session=False)

    db.delete(team_obj)
    db.commit()
