import pytest
from pydantic import ValidationError

from app.schemas.custom_field import CustomFieldBase, TaskCustomFieldValueBase


def test_custom_field_base_valid_type():
    result = CustomFieldBase(name="CF", type="string")
    assert result.type.value == "string"


def test_custom_field_base_empty_name():
    with pytest.raises(ValidationError):
        CustomFieldBase(name="", type="string")


def test_custom_field_base_invalid_type():
    with pytest.raises(ValidationError):
        CustomFieldBase(name="test", type="unknown")


@pytest.mark.parametrize("value", [0, -1])
def test_task_custom_field_value_base_non_positive_custom_field_id(value: int):
    with pytest.raises(ValidationError):
        TaskCustomFieldValueBase(custom_field_id=value)
