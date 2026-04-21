from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8"
    )

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "db"
    DATABASE_URL: str | None = None

    POSTGRES_DB_TEST: str = "db_test"
    DATABASE_TEST_URL: str | None = None

    SUPERUSER_EMAIL: str | None = None

    access_token_expire_minutes: int = 30
    access_token_secret_key: SecretStr
    access_token_algorithm: str = "HS256"

    responses_per_page: int = 10

    YOUTUBE_APP_API_KEY: str | None = None

    GOOGLE_APP_CLIENT_ID: str | None = None

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


settings = Settings()  # type: ignore[call-arg]
