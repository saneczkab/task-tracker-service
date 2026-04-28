import pytest
from pydantic import ValidationError

from app.schemas.stream import StreamCreate, StreamUpdate


def test_stream_create_non_empty_name():
    result = StreamCreate(name="Stream")
    assert result.name == "Stream"


def test_stream_create_empty_name():
    with pytest.raises(ValidationError):
        StreamCreate(name="")


@pytest.mark.parametrize("pos", [-1, -100])
def test_stream_create_negative_position(pos: int):
    with pytest.raises(ValidationError):
        StreamCreate(name="Stream", position=pos)


def test_stream_update_empty_payload():
    result = StreamUpdate()
    assert result.name is None
    assert result.position is None


def test_stream_update_empty_name():
    with pytest.raises(ValidationError):
        StreamUpdate(name="")


@pytest.mark.parametrize("pos", [-1, -100])
def test_stream_update_negative_position(pos: int):
    with pytest.raises(ValidationError):
        StreamUpdate(position=pos)
