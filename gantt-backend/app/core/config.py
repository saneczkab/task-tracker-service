from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    DATABASE_URL: str

    model_config = {
        "env_file": "../.env",
        "env_prefix": "AUTH_",
        "extra": "allow"
    }


settings = Settings()