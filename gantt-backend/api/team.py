from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from models import Project, Stream
from models.team import Team, UserTeam
from models.user import User
from schemas.team import UserWithRoleResponse, TeamCreate, TeamUpdate
from .auth import get_current_user

router = APIRouter()


class RoleId(Enum):
    READER = "Reader"
    EDITOR = "Editor"


ROLE_MAPPING = {
    1: RoleId.READER,
    2: RoleId.EDITOR,
}


@router.get("/api/team/{team_id}/users", response_model=List[UserWithRoleResponse], status_code=status.HTTP_200_OK)
def get_team_users(team_id: int, current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    """Получить всех пользователей в команде team_id"""
    team = data_base.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == team_id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой команде")

    team_members = data_base.query(UserTeam).filter(UserTeam.team_id == team_id).all()

    users_response = []
    for member in team_members:
        role_id = member.role_id
        role = ROLE_MAPPING.get(role_id, RoleId.READER)
        role_name = role.value

        users_response.append(UserWithRoleResponse(
            id=member.user.id,
            email=member.user.email,
            nickname=member.user.nickname,
            role=role_name
        ))

    return users_response


@router.post("/api/team/new", status_code=status.HTTP_201_CREATED)
def create_team(team_data: TeamCreate, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Создание новой команды пользователем user_id"""
    team = Team(name=team_data.name)
    data_base.add(team)
    data_base.flush()

    user_team = UserTeam(
        user_id=current_user.id,
        team_id=team.id,
        role_id=2
    )
    data_base.add(user_team)
    data_base.commit()

    return team


@router.patch("/api/team/{team_id}", status_code=status.HTTP_200_OK)
def update_team(team_id: int, update_data: TeamUpdate, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Частично обновить данные о команде team_id"""
    team = data_base.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == team_id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Вы должны состоять в команде, которую хотите изменить")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на изменение данных команды")

    if update_data.name is not None:
        team.name = update_data.name

    if update_data.newUsers is not None:
        for new_user_email in update_data.newUsers:
            new_user = data_base.query(User).filter(User.email == new_user_email).first()
            if new_user:
                new_member = data_base.query(UserTeam).filter(UserTeam.team_id == team_id,
                                                              UserTeam.user_id == new_user.id).first()
                if not new_member:
                    new_member = UserTeam(
                        user_id=new_user.id,
                        team_id=team_id,
                        role_id=2
                    )
                    data_base.add(new_member)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Пользователь {new_user_email} не найден")

    if update_data.deleteUsers is not None:
        for delete_user_email in update_data.deleteUsers:
            delete_user = data_base.query(User).filter(User.email == delete_user_email).first()
            if delete_user:
                delete_member = data_base.query(UserTeam).filter(UserTeam.team_id == team_id,
                                                                 UserTeam.user_id == delete_user.id).first()
                if delete_member:
                    data_base.delete(delete_member)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Пользователь {delete_user_email} не найден")

    data_base.commit()
    data_base.refresh(team)

    return team


@router.delete("/api/team/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    """Удалить команду team_id"""
    team = data_base.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Команда не найдена")

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == team_id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Вы должны состоять в команде, которую хотите удалить")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на удаление команды")

    projects = data_base.query(Project).filter(Project.team_id == team_id).all()
    project_ids = [proj.id for proj in projects]
    if project_ids:
        data_base.query(Stream).filter(Stream.project_id.in_(project_ids)).delete(synchronize_session=False)
        data_base.query(Project).filter(Project.id.in_(project_ids)).delete(synchronize_session=False)

    data_base.query(UserTeam).filter(UserTeam.team_id == team_id).delete(synchronize_session=False)
    data_base.query(Team).filter(Team.id == team.id).delete(synchronize_session=False)

    data_base.commit()