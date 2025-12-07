from sqlalchemy import orm
from app.models import stream, task, goal
from app.schemas import stream as stream_schemas
from app.core import exception


def get_streams_by_project_id(data_base: orm.Session, proj_id: int):
    """"Получить все стримы по project_id"""
    return data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id).all()


def get_stream_by_id(data_base: orm.Session, stream_id: int):
    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()
    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")
    return stream_obj


def get_stream_by_name_and_proj_id(data_base: orm.Session, name: str, proj_id: int):
    return data_base.query(stream.Stream).filter(stream.Stream.project_id == proj_id,
                                                 stream.Stream.name == name).first()


def create_new_stream(data_base: orm.Session, proj_id: int, stream_data: stream_schemas.StreamCreate):
    new_stream = stream.Stream(name=stream_data.name, project_id=proj_id)
    data_base.add(new_stream)
    data_base.commit()
    data_base.refresh(new_stream)
    return new_stream


def update_stream(data_base: orm.Session, stream_obj: stream.Stream, stream_update_data: stream_schemas.StreamUpdate):
    if stream_update_data.name is not None and stream_update_data.name != stream_obj.name:
        existing_stream = data_base.query(stream.Stream).filter(stream.Stream.project_id == stream_obj.project_id,
                                                                stream.Stream.name == stream_update_data.name,
                                                                stream.Stream.id != stream_obj.id).first()
        if existing_stream:
            raise exception.ConflictError("Стрим с таким названием уже существует в проекте")

        stream_obj.name = stream_update_data.name

    data_base.commit()
    data_base.refresh(stream_obj)

    return stream_obj


def delete_stream(data_base: orm.Session, stream_id: int):
    data_base.query(task.Task).filter(task.Task.stream_id == stream_id).delete(synchronize_session=False)
    data_base.query(goal.Goal).filter(goal.Goal.stream_id == stream_id).delete(synchronize_session=False)

    stream_obj = data_base.query(stream.Stream).filter(stream.Stream.id == stream_id).first()

    if not stream_obj:
        raise exception.NotFoundError("Стрим не найден")

    data_base.delete(stream_obj)
    data_base.commit()
