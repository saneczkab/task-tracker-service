from sqlalchemy import orm

from app.models import goal


def get_goal_by_id(data_base: orm.Session, goal_id: int):
    return data_base.query(goal.Goal).filter(goal.Goal.id == goal_id).first()


def get_goals_by_stream(data_base: orm.Session, stream_id: int):
    return data_base.query(goal.Goal).filter(goal.Goal.stream_id == stream_id).all()


def get_goal_by_name_in_stream(data_base: orm.Session, stream_id: int, name: str, exclude_id: int = None):
    q = data_base.query(goal.Goal).filter(goal.Goal.stream_id == stream_id, goal.Goal.name == name)

    if exclude_id:
        q = q.filter(goal.Goal.id != exclude_id)

    return q.first()


def create_goal(data_base: orm.Session, stream_id: int, goal_data):
    new_goal = goal.Goal(
        name=goal_data.name,
        description=goal_data.description,
        start_date=goal_data.start_date,
        deadline=goal_data.deadline,
        stream_id=stream_id,
        position=goal_data.position
    )

    data_base.add(new_goal)
    data_base.commit()
    data_base.refresh(new_goal)
    return new_goal


def update_goal(data_base: orm.Session, goal_obj, goal_data):
    for field, value in goal_data.model_dump(exclude_unset=True).items():
        setattr(goal_obj, field, value)

    data_base.commit()
    data_base.refresh(goal_obj)
    return goal_obj


def delete_goal(data_base: orm.Session, goal_obj):
    data_base.delete(goal_obj)
    data_base.commit()
