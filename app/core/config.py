from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AI Monitor App"
    DEBUG: bool = False
    ENV: str = "production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_monitor"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Feishu (Lark)
    FEISHU_APP_ID: Optional[str] = None
    FEISHU_APP_SECRET: Optional[str] = None
    FEISHU_WEBHOOK_DEFAULT: Optional[str] = None

    # Scoring weights (percentages, sum should be 100)
    SCORE_WEIGHT_ATTENDANCE: float = 0.20
    SCORE_WEIGHT_PROFESSIONALISM: float = 0.40
    SCORE_WEIGHT_ENGAGEMENT: float = 0.20
    SCORE_WEIGHT_SOFTWARE_SKILL: float = 0.20

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def async_database_url(self) -> str:
        """Ensure async driver is used."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """Return synchronous database URL for Alembic."""
        url = self.DATABASE_URL
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
