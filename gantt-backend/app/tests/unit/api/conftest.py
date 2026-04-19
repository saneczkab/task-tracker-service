from unittest.mock import patch
import pytest

patch("sqlalchemy.sql.schema.MetaData.create_all").start()

from app.core.security import create_access_token


@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "42"})
    return {"Authorization": f"Bearer {token}"}
