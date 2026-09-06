from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://querymind:querymind@localhost:5432/querymind",
        validation_alias="DATABASE_URL",
    )
    secret_key: str = Field(default="change-me-in-development", validation_alias="SECRET_KEY")
    ai_provider: str = Field(default="none", validation_alias="AI_PROVIDER")
    ai_api_key: str | None = Field(default=None, validation_alias="AI_API_KEY")
    ai_model: str = Field(default="", validation_alias="AI_MODEL")
    max_query_rows: int = Field(default=1000, validation_alias="MAX_QUERY_ROWS")
    query_timeout_seconds: int = Field(default=10, validation_alias="QUERY_TIMEOUT_SECONDS")
    max_sql_repair_attempts: int = Field(default=2, validation_alias="MAX_SQL_REPAIR_ATTEMPTS")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", validation_alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def sqlalchemy_database_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
