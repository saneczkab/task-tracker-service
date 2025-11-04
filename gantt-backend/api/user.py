from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from models import User, UserTeam
from schemas.user import UserResponse
from .auth import get_current_user

router = APIRouter()


@router.get("/api/user_by_token", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_token(current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    user_teams = data_base.query(UserTeam).filter(UserTeam.user_id == current_user.id).all()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "teams": [
            {"id": user_team.team.id, "name": user_team.team.name}
            for user_team in user_teams
        ]
    }


@router.get("/api/user/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    """Получить всю инфу о пользователе(никнейм, почта, команды)"""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы можете получить только свои данные")

    requested_user = data_base.query(User).filter(User.id == user_id).first()

    if not requested_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    user_teams = data_base.query(UserTeam).filter(UserTeam.user_id == user_id).all()

    return {
        "id": requested_user.id,
        "email": requested_user.email,
        "nickname": requested_user.nickname,
        "teams": [
            {"id": user_team.team.id, "name": user_team.team.name}
            for user_team in user_teams
        ]

    }


@router.post("/api/user/new")
def create_user():
    """Зарегистрировать пользователя"""
    pass


@router.patch("/api/user/{user_id}")
def update_user(user_id: int, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Частично обновить данные о пользователе user_id"""
    pass


@router.delete("/api/user/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user),
                data_base: Session = Depends(get_db)):
    """Удалить юзер user_id"""
    pass
