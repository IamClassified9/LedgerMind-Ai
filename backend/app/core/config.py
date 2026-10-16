from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LedgerMind AI"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/ledgermind_ai"
    )
    cors_origins: str = "http://localhost:5173"
    gemma_api_key: str = ""
    gemma_model: str = "gemma-3-4b-it"
    gemma_api_base: str = "https://generativelanguage.googleapis.com/v1beta"
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
