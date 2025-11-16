import typing
import fastapi
from sqlalchemy import orm
from app.core import db
from app.models import user, project, team, stream
from app.schemas import stream as stream_schemas
from app.api import auth

router = fastapi.APIRouter()


@router.get("/api/project/{proj_id}/streams", response_model=typing.List[stream_schemas.StreamResponse],
            status_code=fastapi.status.HTTP_200_OK)
def get_project_streams(proj_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                        data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить все стримы в проекте proj_id"""
    project_obj = data_base.query(project.Project).filter(project.Project.id == proj_id).first()

    if not project_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этой команде")

    streams = data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).all()

    return streams


@router.get("/api/stream/{stream_id}", response_model=stream_schemas.StreamResponse,
            status_code=fastapi.status.HTTP_200_OK)
def get_stream(stream_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
               data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Получить информацию о стриме stream_id"""
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

    if not stream_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Стрим не найден")

    project_obj = data_base.query(project.Project).filter(project.Project.id == stream_obj.project_id).first()
    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()
    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этому стриму")

    return stream_obj


@router.post("/api/project/{proj_id}/stream/new", response_model=stream_schemas.StreamResponse,
             status_code=fastapi.status.HTTP_201_CREATED)
def create_stream(proj_id: int, stream_data: stream_schemas.StreamCreate,
                  current_user: user.User = fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Создать новый стрим в проекте proj_id"""
    project_obj = data_base.query(project.Project).filter(project.Project.id == proj_id).first()

    if not project_obj:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Проект не найден")

    user_team = data_base.query(team.UserTeam).filter(team.UserTeam.team_id == project_obj.team_id,
                                                      team.UserTeam.user_id == current_user.id).first()

    if not user_team:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет доступа к этой команде")

    if user_team.role_id != 2:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                    detail="У вас нет прав на создание стримов в этой команде")

    existing_stream = data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id,
                                                            stream.Stream.name == stream_data.name).first()

    if existing_stream:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                    detail="В данном проекте уже есть стрим с таким названием")

    new_stream = stream.Stream(name=stream_data.name, project_id=proj_id)
    data_base.add(new_stream)
    data_base.commit()
    data_base.refresh(new_stream)

    return new_stream


@router.patch("/api/stream/{stream_id}", response_model=stream_schemas.StreamResponse,
              status_code=fastapi.status.HTTP_200_OK)
def update_stream(stream_id: int, stream_update_data: stream_schemas.StreamUpdate,
                  current_user: user.User = fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Частично обновить данные о стриме stream_id"""
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
                                    detail="У вас нет прав на редактирование стримов в этой команде")

    if stream_update_data.name is not None:
        if stream_update_data.name != stream_obj.name:
            existing_stream = data_base.query(stream.Stream).filter(stream.Stream.project_id == stream_obj.project_id,
                                                                    stream.Stream.name == stream_update_data.name,
                                                                    stream.Stream.id != stream_id).first()
            if existing_stream:
                raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                            detail="Стрим с таким названием уже существует в проекте")

            stream_obj.name = stream_update_data.name

    data_base.commit()
    data_base.refresh(stream_obj)

    return stream_obj


@router.delete("/api/stream/{stream_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_stream(stream_id: int, current_user: user.User = fastapi.Depends(auth.get_current_user),
                  data_base: orm.Session = fastapi.Depends(db.get_db)):
    """Удалить стрим stream_id"""
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
                                    detail="У вас нет прав на удаление стримов в этой команде")

    data_base.delete(stream_obj)
    data_base.commit()
