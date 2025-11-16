import enum
import typing
import fastapi
from sqlalchemy import orm
from app.core import db
from app.models import project, stream, team, user
from app.schemas import team as team_schemas
from app.api import auth

router = fastapi.APIRouter()


class RoleId(enum.Enum):
    READER = "Reader"
    EDITOR = "Editor"


ROLE_MAPPING = {
    1: RoleId.READER.value,
    2: RoleId.EDITOR.value,
}


@router.get("/api/team/{team_id}/users", response_model=typing.List[team_schemas.UserWithRoleResponse], status_code=fastapi.status.HTTP_200_OK)
def get_team_users(team_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user), data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить всех пользователей в команде team_id"""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()

    if not team_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                 team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой команде")

    team_members = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id).all()

    users_response = []
    for member in team_members:
        role_id = member.role_id
        role_name = ROLE_MAPPING.get(role_id, RoleId.READER.value)

        users_response.append(team_schemas.UserWithRoleResponse(
            id=member.user.id,
            email=member.user.email,
            nickname=member.user.nickname,
            role=role_name
        ))

    return users_response


@router.post("/api/team/new", status_code=fastapi.status.HTTP_201_CREATED)
def create_team(team_data: team_schemas.TeamCreate, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Создание новой команды пользователем user_id"""
    team_obj = team.Team(name=team_data.name)
    data_base.add(team_obj)
    data_base.flush()

    user_team = team.UserTeam(
        user_id=current_user.id,
        team_id=team_obj.id,
        role_id=2
    )
    data_base.add(user_team)
    data_base.commit()

    return team_obj


@router.patch("/api/team/{team_id}", status_code=fastapi.status.HTTP_200_OK)
def update_team(team_id: int, update_data: team_schemas.TeamUpdate, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о команде team_id"""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()
    if not team_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                 team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                            detail="Вы должны состоять в команде, которую хотите изменить")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет прав на изменение данных команды")

    if update_data.name is not None:
        team_obj.name = update_data.name

    if update_data.newUsers is not None:
        for new_user_email in update_data.newUsers:
            new_user = data_base.query(user.User).filter(user.User.email == new_user_email).first()
            if new_user:
                new_member = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                              team.UserTeam.user_id == new_user.id).first()
                if not new_member:
                    new_member = team.UserTeam(
                        user_id=new_user.id,
                        team_id=team_id,
                        role_id=2
                    )
                    data_base.add(new_member)
            else:
                raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"Пользователь {new_user_email} не найден")

    if update_data.deleteUsers is not None:
        for delete_user_email in update_data.deleteUsers:
            delete_user = data_base.query(user.User).filter(user.User.email == delete_user_email).first()
            if delete_user:
                delete_member = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                                 team.UserTeam.user_id == delete_user.id).first()
                if delete_member:
                    data_base.delete(delete_member)
            else:
                raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"Пользователь {delete_user_email} не найден")

    data_base.commit()
    data_base.refresh(team_obj)

    return team_obj


@router.delete("/api/team/{team_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user), data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить команду team_id"""
    team_obj = data_base.query(team.Team).filter(team.Team.id == team_id).first()
    if not team_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id,
                                                 team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                            detail="Вы должны состоять в команде, которую хотите удалить")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="У вас нет прав на удаление команды")

    projects = data_base.query(project.Project).filter(project.Project.team_id == team_id).all()
    project_ids = [proj.id for proj in projects]
    if project_ids:
        data_base.query(stream.Stream).filter(stream.Stream.project_id.in_(project_ids)).delete(synchronize_session=False)
        data_base.query(project.Project).filter(project.Project.id.in_(project_ids)).delete(synchronize_session=False)

    data_base.query(team.UserTeam).filter(team.UserTeam.team_id == team_id).delete(synchronize_session=False)
    data_base.query(team.Team).filter(team.Team.id == team_obj.id).delete(synchronize_session=False)

    data_base.commit()