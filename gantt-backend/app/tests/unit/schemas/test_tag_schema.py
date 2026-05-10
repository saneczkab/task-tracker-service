import pytest
from pydantic import ValidationError

from app.schemas.tag import TagCreate


def test_tag_create_non_empty_name():
    result = TagCreate(name="Tag", color="#AABBCC")
    assert result.name == "Tag"


def test_tag_create_empty_name():
    with pytest.raises(ValidationError):
        TagCreate(name="", color="#AABBCC")
