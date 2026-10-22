"""Validated environment configuration for the bot and worker."""

from functools import cached_property

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    telegram_bot_token: SecretStr
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/trend_finder.db",
        validation_alias="TREND_FINDER_DATABASE_URL",
    )
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    log_dir: str = "logs"
    refresh_countries: str = "US,GB,IR"
    http_user_agent: str = "TrendFinderBot/1.0"

    @field_validator("refresh_countries")
    @classmethod
    def validate_refresh_countries(cls, value: str) -> str:
        """Reject empty entries and normalize the scheduled refresh country list."""
        codes = [code.strip().upper() for code in value.split(",") if code.strip()]
        if not codes:
            raise ValueError("REFRESH_COUNTRIES must contain at least one country code")
        return ",".join(codes)

    @cached_property
    def refresh_country_codes(self) -> list[str]:
        """Return configured scheduled-refresh country codes."""
        return self.refresh_countries.split(",")
