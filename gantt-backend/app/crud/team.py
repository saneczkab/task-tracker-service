from sqlalchemy import orm

from app.models import team, user
from app.models import goal, project as project_model, stream as stream_model, task as task_model
from app.models import custom_field as cf_model, tag as tag_model, push, meta as meta_model
from app.models.task import TaskReminder, TaskRelation


def get_user_team_by_id(data_base: orm.Session, user_id: int, team_id: int):
    """ "Получить user_team по team_id и user_id"""
    return (
        data_base.query(team.UserTeam)
        .filter(team.UserTeam.team_id == team_id, team.UserTeam.user_id == user_id)
        .first()
    )


def get_team_by_id(data_base: orm.Session, team_id: int):
    return data_base.query(team.Team).filter(team.Team.id == team_id).first()


def get_user_team(data_base: orm.Session, team_id: int, user_id: int):
    return (
        data_base.query(team.UserTeam)
        .filter(team.UserTeam.team_id == team_id, team.UserTeam.user_id == user_id)
        .first()
    )


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
    member = team.UserTeam(team_id=team_id, user_id=user_id, role_id=role_id)
    data_base.add(member)
    data_base.commit()
    data_base.refresh(member)
    return member


def delete_member(data_base: orm.Session, team_id: int, user_id: int):
    data_base.query(team.UserTeam).filter(
        team.UserTeam.team_id == team_id, team.UserTeam.user_id == user_id
    ).delete(synchronize_session=False)
    data_base.commit()


def delete_team(data_base: orm.Session, team_obj):
    data_base.delete(team_obj)
    data_base.commit()


def delete_team_with_dependencies(data_base: orm.Session, team_id: int):
    """Удалить команду со всеми проектами, стримами, задачами и их зависимостями"""
    projects = (
        data_base.query(project_model.Project).filter(
            project_model.Project.team_id == team_id
        ).all()
    )
    project_ids = [p.id for p in projects]

    if project_ids:
        streams = (
            data_base.query(stream_model.Stream).filter(
                stream_model.Stream.project_id.in_(project_ids)
            ).all()
        )
        stream_ids = [s.id for s in streams]

        if stream_ids:
            all_tasks = data_base.query(task_model.Task).filter(
                task_model.Task.stream_id.in_(stream_ids)
            ).all()
            task_ids = [t.id for t in all_tasks]

            if task_ids:
                data_base.query(TaskReminder).filter(
                    TaskReminder.task_id.in_(task_ids)
                ).delete(synchronize_session=False)

                data_base.query(TaskRelation).filter(
                    (TaskRelation.task_id_1.in_(task_ids)) |
                    (TaskRelation.task_id_2.in_(task_ids))
                ).delete(synchronize_session=False)

                data_base.query(cf_model.TaskCustomFieldValue).filter(
                    cf_model.TaskCustomFieldValue.task_id.in_(task_ids)
                ).delete(synchronize_session=False)

                data_base.query(tag_model.TaskTag).filter(
                    tag_model.TaskTag.task_id.in_(task_ids)
                ).delete(synchronize_session=False)

                data_base.query(meta_model.UserTask).filter(
                    meta_model.UserTask.task_id.in_(task_ids)
                ).delete(synchronize_session=False)

            data_base.query(task_model.Task).filter(
                task_model.Task.stream_id.in_(stream_ids)
            ).delete(synchronize_session=False)

            data_base.query(goal.Goal).filter(
                goal.Goal.stream_id.in_(stream_ids)
            ).delete(synchronize_session=False)

        data_base.query(stream_model.Stream).filter(
            stream_model.Stream.project_id.in_(project_ids)
        ).delete(synchronize_session=False)

        data_base.query(project_model.Project).filter(
            project_model.Project.id.in_(project_ids)
        ).delete(synchronize_session=False)

    data_base.query(cf_model.CustomField).filter(
        cf_model.CustomField.team_id == team_id
    ).delete(synchronize_session=False)

    data_base.query(tag_model.Tag).filter(
        tag_model.Tag.team_id == team_id
    ).delete(synchronize_session=False)

    team_users = (
        data_base.query(team.UserTeam).filter(
            team.UserTeam.team_id == team_id
        ).all()
    )
    user_ids = [tu.user_id for tu in team_users]

    if user_ids:
        data_base.query(push.PushSubscription).filter(
            push.PushSubscription.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

    data_base.query(team.UserTeam).filter(
        team.UserTeam.team_id == team_id
    ).delete(synchronize_session=False)

    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()
    if team_obj:
        data_base.delete(team_obj)
        data_base.commit()

