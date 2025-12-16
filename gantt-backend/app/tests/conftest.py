from pathlib import Path

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env_and_models():
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)

