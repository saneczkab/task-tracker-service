import fastapi
from sqlalchemy import orm
from app.core import db
from app.models import user, team
from app.schemas import user as user_schemas
from app.api import auth

router = fastapi.APIRouter()


@router.get("/api/user_by_token", response_model=user_schemas.UserResponse, status_code=fastapi.status.HTTP_200_OK)
def get_user_by_token(current_user: user.User = fastapi.Depends(auth.get_current_user),
                      data_base: orm.Session = fastapi.Depends(db.get_db)):
    user_teams = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == current_user.id).all()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "teams": [
            {"id": user_team.team.id, "name": user_team.team.name}
            for user_team in user_teams
        ]
    }


@router.get("/api/user/{user_id}", response_model=user_schemas.UserResponse, status_code=fastapi.status.HTTP_200_OK)
def get_user(user_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
             data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить всю инфу о пользователе(никнейм, почта, команды)"""
    if current_user.id != user_id:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="Вы можете получить только свои данные")

    requested_user = data_base.query(user.User).filter(user.User.id == user_id).first()

    if not requested_user:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    user_teams = data_base.query(team.UserTeam).filter(team.UserTeam.user_id == user_id).all()

    return {
        "id": requested_user.id,
        "email": requested_user.email,
        "nickname": requested_user.nickname,
        "teams": [
            {"id": user_team.team.id, "name": user_team.team.name}
            for user_team in user_teams
        ]
    }


@router.patch("/api/user/{user_id}")
def update_user(user_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о пользователе user_id"""
    pass


@router.delete("/api/user/{user_id}")
def delete_user(user_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить юзер user_id"""
    pass
