import typing
import fastapi
from app.core import db
from app.models import user, stream, project, team, goal
from app.api import auth
from sqlalchemy import orm
from app.schemas import goal as goal_schemas

router = fastapi.APIRouter()


@router.get("/api/stream/{stream_id}/goals", response_model=typing.List[goal_schemas.GoalResponse],
            status_code=fastapi.status.HTTP_200_OK)
def get_stream_goals(stream_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                     data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все цели у стрима stream_id"""
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

    if not stream_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этому стриму")

    goals = data_base.query(goal.Goal).filter(goal.Goal.stream_id == stream_obj.id).all()

    return goals


@router.post("/api/stream/{stream_id}/goal/new", response_model=goal_schemas.GoalResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
def create_goal(stream_id: int, goal_data: goal_schemas.GoalCreate,
                current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Создать цель в стриме stream_id"""
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

    if not stream_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этому стриму")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на создание целей в этом проекте")

    existing_goal = data_base.query(goal.Goal).filter(goal.Goal.stream_id == stream_id,
                                                      goal.Goal.name == goal_data.name).first()

    if existing_goal:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                    detail="В данном стриме уже есть цель с таким названием")

    new_goal = goal.Goal(
        name=goal_data.name,
        stream_id=stream_id,
        description=goal_data.description,
        deadline=goal_data.deadline
    )

    data_base.add(new_goal)
    data_base.commit()
    data_base.refresh(new_goal)

    return new_goal


@router.patch("/api/goal/{goal_id}", response_model=goal_schemas.GoalResponse, status_code=fastapi.status.HTTP_200_OK)
def update_goal(goal_id: int, goal_update_data: goal_schemas.GoalUpdate,
                current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о цели goal_id"""
    goal_obj = data_base.query(goal.Goal).filter(goal.Goal.id == goal_id).first()

    if not goal_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Цель не найдена")

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == goal_obj.stream_id).first()
    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этой цели")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на редактирование целей в этом стриме")

    if goal_update_data.name is not None:
        if goal_update_data.name != goal_obj.name:
            existing_goal = data_base.query(goal.Goal).filter(goal.Goal.name == goal_update_data.name,
                                                              goal.Goal.stream_id == goal_obj.stream_id,
                                                              goal.Goal.id != goal_id).first()

            if existing_goal:
                raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                            detail="Цель с таким названием уже существует в стриме")

            goal_obj.name = goal_update_data.name

    if goal_update_data.description is not None:
        goal_obj.description = goal_update_data.description

    if goal_update_data.deadline is not None:
        goal_obj.deadline = goal_update_data.deadline

    data_base.commit()
    data_base.refresh(goal_obj)

    return goal_obj


@router.delete("/api/goal/{goal_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить цель goal_id"""
    goal_obj = data_base.query(goal.Goal).filter(goal.Goal.id == goal_id).first()

    if not goal_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Цель не найдена")

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == goal_obj.stream_id).first()
    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этой цели")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на удаление целей в этом стриме")

    data_base.delete(goal_obj)
    data_base.commit()
