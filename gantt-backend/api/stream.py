from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from models import User, Project, UserTeam
from models.stream import Stream
from schemas.stream import StreamCreate, StreamUpdate, StreamResponse
from .auth import get_current_user

router = APIRouter()


@router.get("/api/project/{proj_id}/streams", response_model=List[StreamResponse], status_code=status.HTTP_200_OK)
def get_project_streams(proj_id: int, current_user: User = Depends(get_current_user),
                        data_base: Session = Depends(get_db)):
    """Получить все стримы в проекте proj_id"""
    project = data_base.query(Project).filter(Project.id == proj_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой команде")

    streams = data_base.query(Stream).filter(Stream.project_id == proj_id).all()

    return streams


@router.post("/api/project/{proj_id}/stream/new", response_model=StreamResponse, status_code=status.HTTP_201_CREATED)
def create_stream(proj_id: int, stream_data: StreamCreate, current_user: User = Depends(get_current_user),
                  data_base: Session = Depends(get_db)):
    """Создать новый стрим в проекте proj_id"""
    project = data_base.query(Project).filter(Project.id == proj_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этой команде")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на создание стримов в этой команде")

    existing_stream = data_base.query(Stream).filter(Stream.project_id == proj_id,
                                                     Stream.name == stream_data.name).first()

    if existing_stream:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="В данном проекте уже есть стрим с таким названием")

    new_stream = Stream(name=stream_data.name, project_id=proj_id)
    data_base.add(new_stream)
    data_base.commit()
    data_base.refresh(new_stream)

    return new_stream


@router.patch("/api/stream/{stream_id}", response_model=StreamResponse, status_code=status.HTTP_200_OK)
def update_stream(stream_id: int, stream_update_data: StreamUpdate, current_user: User = Depends(get_current_user),
                  data_base: Session = Depends(get_db)):
    """Частично обновить данные о стриме stream_id"""
    stream = data_base.query(Stream).filter(Stream.id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project = data_base.query(Project).filter(Project.id == stream.project_id).first()

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этому стриму")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на редактирование стримов в этой команде")

    if stream_update_data.name is not None:
        if stream_update_data.name != stream.name:
            existing_stream = data_base.query(Stream).filter(Stream.project_id == stream.project_id,
                                                             Stream.name == stream_update_data.name,
                                                             Stream.id != stream_id).first()
            if existing_stream:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="Стрим с таким названием уже существует в проекте")

            stream.name = stream_update_data.name

    data_base.commit()
    data_base.refresh(stream)

    return stream


@router.delete("/api/stream/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stream(stream_id: int, current_user: User = Depends(get_current_user), data_base: Session = Depends(get_db)):
    """Удалить стрим stream_id"""
    stream = data_base.query(Stream).filter(Stream.id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project = data_base.query(Project).filter(Project.id == stream.project_id).first()

    user_team = data_base.query(UserTeam).filter(UserTeam.team_id == project.team.id,
                                                 UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этому стриму")

    if user_team.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="У вас нет прав на удаление стримов в этой команде")

    data_base.delete(stream)
    data_base.commit()
