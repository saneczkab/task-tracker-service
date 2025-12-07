from sqlalchemy import orm

from app.models import team, user


def get_user_team_by_id(data_base: orm.Session, user_id: int, team_id: int):
    """"Получить user_team по team_id и user_id"""
    return data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                 team.UserTeam.user_id == user_id).first()


def get_team_by_id(data_base: orm.Session, team_id: int):
    return data_base.query(team.Team).filter(team.Team.id == team_id).first()


def get_user_team(data_base: orm.Session, team_id: int, user_id: int):
    return data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                 team.UserTeam.user_id == user_id).first()


def get_team_users(data_base: orm.Session, team_id: int):
    return data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id).all()


def get_teams_by_user(data_base: orm.Session, user_id: int):
    teams = (
        data_base.query(team.Team)
        .join(team.UserTeam, team.UserTeam.team_id == team.Team.id)
        .filter(team.UserTeam.user_id == user_id)
        .all()
    )

    return teams


def get_user_by_email(data_base: orm.Session, email: str):
    return data_base.query(user.User).filter(user.User.email == email).first()


def create_team(data_base: orm.Session, name: str):
    team_obj = team.Team(name=name)
    data_base.add(team_obj)
    data_base.commit()
    data_base.refresh(team_obj)
    return team_obj


def add_user_to_team(data_base: orm.Session, team_id: int, user_id: int, role_id: int):
    member = team.UserTeam(
        team_id=team_id,
        user_id=user_id,
        role_id=role_id
    )
    data_base.add(member)
    data_base.commit()
    data_base.refresh(member)
    return member


def delete_member(data_base: orm.Session, team_id: int, user_id: int):
    data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id, team.UserTeam.user_id == user_id).delete(
        synchronize_session=False)
    data_base.commit()


def delete_team(data_base: orm.Session, team_obj):
    data_base.delete(team_obj)
    data_base.commit()
