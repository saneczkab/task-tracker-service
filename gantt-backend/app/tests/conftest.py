import os
import pytest
from pathlib import Path
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env_and_models():
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)

    import app.models.goal
    import app.models.task
    import app.models.meta